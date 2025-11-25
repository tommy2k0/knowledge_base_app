from pydantic import BaseModel
from datetime import datetime

from .tag import TagRead

class ArticleBase(BaseModel):
    title: str
    content: str

class ArticleCreate(ArticleBase):
    tags: list[str] | None = None

class ArticleRead(ArticleBase):
    id: int
    author_id: int
    tags: list[TagRead] | None = None
    created_at: datetime

    class Config:
        orm_mode = True

