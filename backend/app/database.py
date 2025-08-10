from typing import Iterator
from sqlmodel import SQLModel, create_engine, Session
from .config import get_settings


def _normalize_database_url(url: str) -> str:
    # Allow Railway style postgres URLs and ensure psycopg driver
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


settings = get_settings()
_db_url = _normalize_database_url(settings.database_url)
engine = create_engine(
    _db_url,
    echo=False,
    connect_args={"check_same_thread": False} if _db_url.startswith("sqlite") else {},
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session 