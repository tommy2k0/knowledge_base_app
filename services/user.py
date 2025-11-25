from ..repositories.user import UserRepository
from ..schemas.user import UserCreate
from ..models.user import User

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        return self.repo.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> User | None:
        return self.repo.get_by_email(email)

    def register_user(self, user: UserCreate) -> User:
        return self.repo.create(user)
    
    def login_user(self, username: str, password: str) -> User | None:
        return self.repo.login(username, password)
    
    def list_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        return self.repo.list(skip=skip, limit=limit)

    def update_user_role(self, user_id: int, role: str) -> User | None:
        return self.repo.update_role(user_id, role)