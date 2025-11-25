from fastapi import Cookie
from fastapi.responses import RedirectResponse
from datetime import datetime
import os

from fastapi import Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..repositories.user import UserRepository
from ..services.user import UserService
from ..repositories.user import UserRepository
from ..services.user import UserService
from ..repositories.session import SessionRepository
from ..services.session import SessionService
from ..repositories.article import ArticleRepository
from ..services.article import ArticleService
from ..services.comment import CommentService
from ..repositories.comment import CommentRepository
from ..services.embedding import EmbeddingService
from ..services.search import SearchService
from ..repositories.chat import ChatRepository
from ..services.chat import ChatService

# Load from environment variables
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

if not AZURE_OPENAI_API_BASE or not AZURE_OPENAI_API_KEY:
    raise EnvironmentError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set in environment variables.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

def get_session_repository(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)

def get_session_service(repo: SessionRepository = Depends(get_session_repository)) -> SessionService:
    return SessionService(repo)

def get_article_repository(db: Session = Depends(get_db)) -> ArticleRepository:
    return ArticleRepository(db)

def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(api_key=AZURE_OPENAI_API_KEY, azure_endpoint=AZURE_OPENAI_API_BASE)

def get_article_service(repo: ArticleRepository = Depends(get_article_repository), embedding_service: EmbeddingService = Depends(get_embedding_service)) -> ArticleService:
    return ArticleService(repo, embedding_service)

def get_comment_repository(db: Session = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)

def get_comment_service(repo: CommentRepository = Depends(get_comment_repository)) -> CommentService:
    return CommentService(repo)

def get_search_service(
    article_repo: ArticleRepository = Depends(get_article_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> SearchService:
    return SearchService(article_repo, embedding_service)

def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)

def get_chat_service(repo: ChatRepository = Depends(get_chat_repository), search_service: SearchService = Depends(get_search_service), azure_openai_key: str = AZURE_OPENAI_API_KEY, azure_openai_endpoint: str = AZURE_OPENAI_API_BASE) -> ChatService:
    return ChatService(repo, search_service, azure_openai_key, azure_openai_endpoint)

def get_current_user(
    session_token: str = Cookie(None),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
) -> User:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    session = session_service.get_session_by_token(session_token)
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    user = user_service.get_user_by_id(session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def get_current_user_or_redirect(
    session_token: str = Cookie(None),
    session_service: SessionService = Depends(get_session_service),
    user_service: UserService = Depends(get_user_service),
):
    if not session_token:
        return RedirectResponse(url="/login")
    session = session_service.get_session_by_token(session_token)
    if not session or session.expires_at < datetime.utcnow():
        return RedirectResponse(url="/login")
    user = user_service.get_user_by_id(session.user_id)
    if not user:
        return RedirectResponse(url="/login")
    return user

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_dependency
