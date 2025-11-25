from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..schemas.article import ArticleCreate, ArticleRead
from ..repositories.article import ArticleRepository
from ..services.article import ArticleService
from ..services.search import SearchService
from ..models.user import User
from ..core.deps import get_article_service, require_role, get_current_user, get_search_service

router = APIRouter()


@router.post("/articles", response_model=ArticleRead)
def create_article(article: ArticleCreate, service: ArticleService = Depends(get_article_service), current_user = Depends(get_current_user)):
    author_id = current_user.id
    return service.create_article(article, author_id)

@router.get("/articles", response_model=list[ArticleRead])
def list_articles(skip: int = 0, limit: int = 10, tags: list[str] = Query(None), service: ArticleService = Depends(get_article_service)):
    return service.list_articles(skip=skip, limit=limit, tags=tags)

@router.get("/articles/search", response_model=list[ArticleRead])
def search_articles(query: str, top_k: int = 5, search_service: SearchService = Depends(get_search_service)):
    results = search_service.search_articles(query, top_k=top_k)
    articles = [article for article, score in results]
    return articles

@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, service: ArticleService = Depends(get_article_service)):
    db_article = service.get_article(article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@router.put("/articles/{article_id}", response_model=ArticleRead)
def update_article(article_id: int, article: ArticleCreate, service: ArticleService = Depends(get_article_service), current_user = Depends(get_current_user)):
    db_article = service.get_article(article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this article")
    updated_article = service.update_article(article_id, article)
    if not updated_article:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated_article

@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, service: ArticleService = Depends(get_article_service), current_user = Depends(get_current_user)):
    db_article = service.get_article(article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if db_article.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this article")
    success = service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return None

@router.get("/admin-only")
def admin_endpoint(current_user: User = Depends(require_role("admin"))):
    return {"message": "This is an admin-only endpoint."}
