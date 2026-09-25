"""SQLAlchemy database engine and session factory for PostgreSQL."""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

logger = logging.getLogger("railopt.db")

# Force SQLAlchemy to explicitly use standard psycopg2 instead of psycopg v3
safe_db_url = settings.DATABASE_URL
if safe_db_url.startswith("postgresql://"):
    safe_db_url = safe_db_url.replace("postgresql://", "postgresql+psycopg2://")
elif safe_db_url.startswith("postgresql+psycopg://"):
    safe_db_url = safe_db_url.replace("postgresql+psycopg://", "postgresql+psycopg2://")
elif safe_db_url.startswith("postgres://"):
    safe_db_url = safe_db_url.replace("postgres://", "postgresql+psycopg2://")

engine = create_engine(
    safe_db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    use_insertmanyvalues=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a database session and ensure closure on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
