from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.chat import ChatSessionCreate, ChatMessageCreate, ChatSessionRead, ChatMessageRead, ChatRequest, ChatResponse
from ..services.chat import ChatService
from ..models.user import User
from ..core.deps import get_chat_service, get_current_user
import json

router = APIRouter()


@router.post("/chat/sessions", response_model=ChatSessionRead, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_data: ChatSessionCreate,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session for the current user."""
    return chat_service.create_session(current_user.id, session_data.title)

@router.get("/chat/sessions", response_model=list[ChatSessionRead])
def list_chat_sessions(
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user)
):
    """List all chat sessions for the current user."""
    return chat_service.list_user_sessions(current_user.id)

@router.get("/chat/sessions/{session_id}", response_model=ChatSessionRead)
def get_chat_session(
    session_id: int,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat session by ID."""
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat session")
    return session

@router.get("/chat/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
def get_session_messages(
    session_id: int,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user)
):
    """Get all messages for a specific chat session."""
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat session")
    return chat_service.get_session_messages(session_id)

@router.post("/chat/sessions/{session_id}/messages", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    session_id: int,
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user)
):
    """Send a message and get AI response with RAG."""
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat session")
    
    assistant_message, source_ids = chat_service.send_message(session_id, chat_request.message)
    return ChatResponse(message=assistant_message, sources=source_ids)