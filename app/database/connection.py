"""Database connection manager"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.config import Config
from .models import Base

# Global session maker
_SessionLocal = None
_engine = None


def init_db():
    """Initialize database connection"""
    global _engine, _SessionLocal

    if Config.DB_TYPE == "turso":
        # Turso uses libsql protocol
        db_url = Config.DATABASE_URL
        if db_url and not db_url.startswith("sqlite"):
            # Convert libsql:// to sqlite:// for SQLAlchemy
            db_url = db_url.replace("libsql://", "sqlite:///")
    else:
        db_url = Config.DATABASE_URL

    _engine = create_engine(
        db_url,
        echo=Config.DEBUG,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    return _engine


@contextmanager
def get_db() -> Session:
    """Get database session with context manager"""
    if _SessionLocal is None:
        init_db()

    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_session() -> Session:
    """Get database session"""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()
