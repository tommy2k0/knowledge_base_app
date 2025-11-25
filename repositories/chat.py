from sqlalchemy.orm import Session
from ..models.chat import ChatSession, ChatMessage


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, title: str | None = None) -> ChatSession:
        chat_session = ChatSession(user_id=user_id, title=title)
        self.db.add(chat_session)
        self.db.commit()
        self.db.refresh(chat_session)
        return chat_session

    def get_session(self, session_id: int) -> ChatSession | None:
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def list_user_sessions(self, user_id: int) -> list[ChatSession]:
        return self.db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()

    def add_message(self, session_id: int, role: str, content: str, sources: str | None = None) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content, sources=sources)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(self, session_id: int) -> list[ChatMessage]:
        return self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
