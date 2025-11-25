from sqlalchemy.orm import Session
from datetime import datetime
from ..models.user import UserSession
from ..schemas.user import UserCreate

class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, session_token: str, expires_at) -> UserSession:
        db_session = UserSession(user_id=user_id, session_token=session_token, expires_at=expires_at)
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def get_session_by_token(self, session_token: str) -> UserSession | None:
        return self.db.query(UserSession).filter(UserSession.session_token == session_token).first()

    def get_session_by_user_id(self, user_id: int) -> UserSession | None:
        db_sessions = self.db.query(UserSession).filter(UserSession.user_id == user_id).all()
        for session in db_sessions:
            if session.expires_at > datetime.utcnow():
                return session
        return None

    def delete_session(self, session_token: str) -> bool:
        db_session = self.get_session_by_token(session_token)
        if not db_session:
            return False
        self.db.delete(db_session)
        self.db.commit()
        return True
