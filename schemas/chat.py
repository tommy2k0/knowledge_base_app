from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ChatSessionBase(BaseModel):
    title: str | None = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionRead(ChatSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    
class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageRead(ChatMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str  # e.g., "user" or "assistant"
    sources: str | None = None
    created_at: datetime


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: ChatMessageRead
    sources: list[int] | None = None  # List of article IDs used as sources
    