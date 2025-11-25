from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.session import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    articles = relationship("Article", secondary="article_tags", back_populates="tags")