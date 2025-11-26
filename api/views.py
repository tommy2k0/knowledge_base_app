"""
HTML view routes - serving templates with HTMX
"""
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Response, status, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from uuid import uuid4
from ..core.deps import get_current_user_or_redirect, get_user_service, get_session_service
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin
from ..services.user import UserService
from ..services.session import SessionService
import os

router = APIRouter()

# Use absolute path to templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Use secure cookies only in production
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page - redirect to chat or login"""
    return RedirectResponse(url="/login")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, user: User = Depends(get_current_user_or_redirect)):
    """Main chat interface - requires authentication"""
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})

@router.get("/articles", response_class=HTMLResponse)
async def articles_page(request: Request, session_token: str = Cookie(None), session_service: SessionService = Depends(get_session_service), user_service: UserService = Depends(get_user_service)):
    """Articles browser page - requires authentication"""
    # check if user is authenticated
    if not session_token:
        return RedirectResponse(url="/login")
    
    # validate session token
    session = session_service.get_session_by_token(session_token)
    if not session or session.expires_at < datetime.now(timezone.utc):
        return RedirectResponse(url="/login")
    
    # get user
    user = user_service.get_user_by_id(session.user_id)
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("articles.html", {"request": request, "user": user})

@router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    """Logout and redirect to login"""
    response = RedirectResponse(url="/login")
    response.delete_cookie("session_token")
    return response


# Form submission endpoints (accept form data, call API services)
@router.post("/form/signup")
async def signup_form(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    service: UserService = Depends(get_user_service)
):
    """Handle signup form submission"""
    try:
        user_data = UserCreate(username=username, email=email, password=password, full_name=full_name)
        existing_user = service.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        existing_email = service.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user = service.register_user(user_data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "Account created successfully", "username": user.username}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/form/login")
async def login_form(
    username: str = Form(...),
    password: str = Form(...),
    user_service: UserService = Depends(get_user_service),
    session_service: SessionService = Depends(get_session_service)
):
    """Handle login form submission"""
    db_user = user_service.login_user(username, password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    session = session_service.create_session(db_user.id, session_token=str(uuid4()))
    json_response = JSONResponse(
        content={
            "message": "Login successful",
            "username": db_user.username,
            "redirect": "/chat"
        }
    )
    json_response.set_cookie(
        key="session_token", 
        value=session.session_token, 
        httponly=True, 
        secure=IS_PRODUCTION,
        samesite="lax",
    )
    return json_response
