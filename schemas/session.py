from pydantic import BaseModel
from datetime import datetime

class SessionBase(BaseModel):
    user_id: int
    session_token: str
    expires_at: datetime

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
