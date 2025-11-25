import json
import numpy as np

from ..repositories.article import ArticleRepository
from .embedding import EmbeddingService
from ..models.article import Article

class SearchService:
    def __init__(self, article_repo: ArticleRepository, embedding_service: EmbeddingService):
        self.article_repo = article_repo
        self.embedding_service = embedding_service

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(vec1)
        b = np.array(vec2)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_articles(self, query: str, top_k: int = 5) -> list[tuple[Article, float]]:
        """
        Search for articles most relevant to the query.
        Returns list of tuples (Article, similarity_score).
        """
        # Generate embedding for the query
        query_embedding = self.embedding_service.generate_embedding(query)

        # Get all articles with embeddings
        articles = self.article_repo.list_articles(skip=0, limit=1000)

        # Calculate similarity scores
        results = []
        for article in articles:
            if article.embedding:
                article_embedding = self.embedding_service.json_to_embedding(article.embedding)
                similarity = self.cosine_similarity(query_embedding, article_embedding)
                results.append((article, similarity))
        
        # Sort results by similarity score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]