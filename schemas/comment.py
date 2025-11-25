from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    article_id: int
    content: str

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CommentReplyBase(BaseModel):
    content: str

class CommentReplyCreate(CommentReplyBase):
    pass

class CommentReplyRead(CommentReplyBase):
    id: int
    comment_id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True
