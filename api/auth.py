from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import os
from ..schemas.user import UserCreate, UserRead, UserLogin
from ..repositories.user import UserRepository
from ..services.user import UserService
from ..repositories.session import SessionRepository
from ..services.session import SessionService
from ..models.user import User
from ..core.deps import get_user_service, get_session_service, get_current_user

router = APIRouter()

# Use secure cookies only in production
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, service: UserService = Depends(get_user_service)):
    existing_user = service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    existing_email = service.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return service.register_user(user)

@router.post("/login", response_model=UserRead)
def login(response: Response, user: UserLogin, user_service: UserService = Depends(get_user_service), session_service: SessionService = Depends(get_session_service)):
    db_user = user_service.login_user(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    session = session_service.create_session(db_user.id, session_token=str(uuid4()))
    response.set_cookie(
        key="session_token", 
        value=session.session_token, 
        httponly=True, 
        secure=IS_PRODUCTION,  # Only require HTTPS in production
        samesite="lax"
    )
    return db_user

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(response: Response, session_token: str = Cookie(None), session_service: SessionService = Depends(get_session_service)):
    if session_token:
        session_service.delete_session(session_token)
        response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}
