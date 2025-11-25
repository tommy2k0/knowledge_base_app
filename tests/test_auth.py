"""
Tests for authentication endpoints.
"""
import pytest


def test_signup_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/signup",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123"
        }
    )
    assert response.status_code == 201  # Created
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"
    assert "id" in data


def test_signup_duplicate_username(client, test_user):
    """Test signup with existing username fails."""
    response = client.post(
        "/api/v1/signup",
        json={
            "username": "testuser",  # Already exists
            "email": "different@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_signup_duplicate_email(client, test_user):
    """Test signup with existing email fails."""
    response = client.post(
        "/api/v1/signup",
        json={
            "username": "differentuser",
            "email": "test@example.com",  # Already exists
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    # Check that session cookie is set
    assert "session_token" in response.cookies


def test_login_wrong_password(client, test_user):
    """Test login with wrong password fails."""
    response = client.post(
        "/api/v1/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent username fails."""
    response = client.post(
        "/api/v1/login",
        json={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == 401


def test_get_current_user(authenticated_client):
    """Test getting current user info."""
    response = authenticated_client.get("/api/v1/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthenticated(client):
    """Test getting current user without authentication fails."""
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()


def test_logout(authenticated_client):
    """Test logout functionality."""
    response = authenticated_client.post("/api/v1/logout")
    assert response.status_code == 200
    
    # Verify session is invalidated
    response = authenticated_client.get("/api/v1/me")
    assert response.status_code == 401
