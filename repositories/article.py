from sqlalchemy.orm import Session
from ..models.article import Article
from ..models.tag import Tag
from ..schemas.article import ArticleCreate

class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, article_id: int) -> Article | None:
        return self.db.query(Article).filter(Article.id == article_id).first()
    
    def list_articles(self, skip: int = 0, limit: int = 10, tags: list[str] | None = None) -> list[Article]:
        query = self.db.query(Article)
        if tags:
            query = query.filter(Article.tags.any(Tag.name.in_(tags)))
        return query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, article: ArticleCreate, author_id: int, embedding: list[float] | None = None) -> Article:
        tag_objs = []
        if article.tags:
            for tag_name in article.tags:
                tag = self.db.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                    self.db.flush() # Ensure tag gets an ID
                tag_objs.append(tag)
        db_article = Article(
            title=article.title, 
            content=article.content, 
            embedding=embedding,
            author_id=author_id,
            tags=tag_objs,
        )
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article

    def update(self, article_id: int, article: ArticleCreate, embedding: list[float] | None = None) -> Article | None:
        db_article = self.get(article_id)
        if not db_article:
            return None
        for key, value in article.dict().items():
            if key == "tags":
                tag_objs = []
                if value:
                    for tag_name in value:
                        tag = self.db.query(Tag).filter_by(name=tag_name).first()
                        if not tag:
                            tag = Tag(name=tag_name)
                            self.db.add(tag)
                            self.db.flush() # Ensure tag gets an ID
                        tag_objs.append(tag)
                setattr(db_article, "tags", tag_objs)
            else:
                setattr(db_article, key, value)
        if embedding is not None:
            db_article.embedding = embedding
        self.db.commit()
        self.db.refresh(db_article)
        return db_article
    
    def delete(self, article_id: int) -> bool:
        db_article = self.get(article_id)
        if not db_article:
            return False
        self.db.delete(db_article)
        self.db.commit()
        return True