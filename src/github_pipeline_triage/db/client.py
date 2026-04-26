"""SQLite database client."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from github_pipeline_triage.db.schema import Base

DATABASE_URL = "sqlite:///triage.db"
ECHO = False


engine = create_engine(
    DATABASE_URL,
    echo=ECHO,
    connect_args={"check_same_thread": False},
)

event.listen(
    engine,
    "connect",
    lambda conn, _: conn.execute("PRAGMA journal_mode=WAL"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
