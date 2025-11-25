from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import hash_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hash_password(user.password),
            role=user.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def login(self, username: str, password: str) -> User | None:
        user = self.get_by_username(username)
        if user and user.hashed_password == hash_password(password):
            return user
        return None
    
    def list(self, skip: int = 0, limit: int = 10) -> list[User]:
        return self.db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_role(self, user_id: int, role: str) -> User | None:
        user = self.get_by_id(user_id)
        if user:
            user.role = role
            self.db.commit()
            self.db.refresh(user)
            return user
        return None