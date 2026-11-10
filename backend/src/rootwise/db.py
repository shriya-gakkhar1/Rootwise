"""Database engine, sessions, and declarative model base."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


def make_engine(database_url: str) -> Engine:
    """Create an SQLAlchemy engine for the configured database."""
    if database_url == "sqlite:///:memory:":
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(database_url, pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create short-lived database sessions for API operations."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
