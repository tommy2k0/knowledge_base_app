import os
from dotenv import load_dotenv

# Load .env file in development
load_dotenv()

from fastapi import FastAPI
from .db.session import engine, Base
from .api import articles, auth, users, comments, chat, views

def create_app() -> FastAPI:
    app = FastAPI(title="Knowledge Base API")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Include API routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(articles.router, prefix="/api/v1")
    app.include_router(comments.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(views.router)

    # Health check for Railway
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()


# uvicorn knowledge_base_app.main:app --reload
