"""FastAPI application factory and health endpoint."""

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .config import Settings, get_settings
from .db import make_engine


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the RootWise API application."""
    runtime_settings = settings or get_settings()
    engine = make_engine(runtime_settings.database_url)
    app = FastAPI(title="RootWise API")

    @app.get("/health")
    def health() -> dict[str, bool | str]:
        """Report API availability and whether the database accepts a connection."""
        database_ok = False
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                database_ok = True
        except SQLAlchemyError:
            database_ok = False
        return {"status": "ok", "db": database_ok}

    return app
