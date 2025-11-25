import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Use PostgreSQL for production, SQLite in development
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    FILE_PATH = Path(__file__).parent.parent
    DATABASE_URL = f"sqlite:///{FILE_PATH}/test.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Railway provides postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
