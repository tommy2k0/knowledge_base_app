from ..repositories.article import ArticleRepository
from ..schemas.article import ArticleCreate
from ..models.article import Article
from .embedding import EmbeddingService

class ArticleService:
    def __init__(self, repo: ArticleRepository, embedding_service: EmbeddingService):
        self.repo = repo
        self.embedding_service = embedding_service

    def get_article(self, article_id: int) -> Article | None:
        return self.repo.get(article_id)

    def list_articles(self, skip: int = 0, limit: int = 10, tags: list[str] | None = None) -> list[Article]:
        return self.repo.list_articles(skip=skip, limit=limit, tags=tags)

    def create_article(self, article: ArticleCreate, author_id: int) -> Article:
        embedding = self.embedding_service.generate_embedding(article.content)
        embedding = self.embedding_service.embedding_to_json(embedding)
        return self.repo.create(article, author_id, embedding=embedding)

    def update_article(self, article_id: int, article: ArticleCreate) -> Article | None:
        embedding = self.embedding_service.generate_embedding(article.content)
        embedding = self.embedding_service.embedding_to_json(embedding)
        return self.repo.update(article_id, article, embedding=embedding)

    def delete_article(self, article_id: int) -> bool:
        return self.repo.delete(article_id)