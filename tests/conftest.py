"""
Pytest configuration and fixtures for testing.
"""
import pytest
import sys
from pathlib import Path

# # Add parent directory to path for package imports
# parent_dir = Path(__file__).parent.parent.parent
# sys.path.insert(0, str(parent_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from knowledge_base_app.db.base import Base
from knowledge_base_app.main import app
from knowledge_base_app.core.deps import get_db
from knowledge_base_app.models.user import User
from knowledge_base_app.core.security import hash_password

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    # test_user is already created in the db_session
    # Now login to get session cookie
    response = client.post(
        "/api/v1/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        print(f"Cookies after login: {client.cookies}")
    assert response.status_code == 200, f"Login failed: {response.json()}"
    # Cookies are automatically persisted in TestClient
    print(f"Session cookie set: {client.cookies}")
    return client


@pytest.fixture
def admin_client(client, test_admin):
    """Create an authenticated admin client."""
    # test_admin is already created in the db_session
    response = client.post(
        "/api/v1/login",
        json={"username": "admin", "password": "adminpass123"}
    )
    if response.status_code != 200:
        print(f"Admin login failed: {response.status_code} - {response.text}")
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    return client
