from ..repositories.session import SessionRepository
from ..schemas.session import SessionCreate, SessionRead
from ..models.user import UserSession
from datetime import datetime, timedelta, timezone

class SessionService:
    def __init__(self, repo: SessionRepository):
        self.repo = repo

    def create_session(self, user_id: int, session_token: str, expires_in_minutes: int = 60) -> UserSession:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        return self.repo.create_session(user_id, session_token, expires_at)

    def get_session_by_token(self, session_token: str) -> UserSession | None:
        return self.repo.get_session_by_token(session_token)

    def get_session_by_user_id(self, user_id: int) -> UserSession | None:
        return self.repo.get_session_by_user_id(user_id)

    def delete_session(self, session_token: str) -> bool:
        return self.repo.delete_session(session_token)