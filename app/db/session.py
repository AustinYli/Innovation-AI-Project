from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.db.models import Base


engine = None
SessionLocal = None
database_error = None


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def get_engine():
    global database_error, engine

    if not DATABASE_URL:
        return None

    if engine is None:
        try:
            engine = create_engine(
                _normalize_database_url(DATABASE_URL),
                pool_pre_ping=True,
            )
            database_error = None
        except ArgumentError as error:
            database_error = str(error)
            return None

    return engine


def get_session_factory():
    global SessionLocal

    if SessionLocal is None:
        active_engine = get_engine()
        if active_engine is None:
            return None
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=active_engine,
        )

    return SessionLocal


def init_db():
    active_engine = get_engine()
    if active_engine is None:
        return False

    try:
        Base.metadata.create_all(bind=active_engine)
        return True
    except SQLAlchemyError as error:
        global database_error
        database_error = str(error)
        return False


def get_database_error():
    return database_error
