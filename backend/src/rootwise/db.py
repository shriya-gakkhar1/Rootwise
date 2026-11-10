"""Database engine and declarative model base."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


def make_engine(database_url: str):
    """Create an SQLAlchemy engine for the configured database."""
    return create_engine(database_url, pool_pre_ping=True)
