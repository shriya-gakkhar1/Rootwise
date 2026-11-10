"""FastAPI application factory and health endpoint."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .config import Settings, get_settings
from .db import make_engine, make_session_factory
from .ingestion.api import build_ingestion_router

MAX_REQUEST_BYTES = 1_048_576


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the RootWise API application."""
    runtime_settings = settings or get_settings()
    engine = make_engine(runtime_settings.database_url)
    app = FastAPI(title="RootWise API")
    app.state.engine = engine

    @app.middleware("http")
    async def enforce_request_size(request: Request, call_next):
        """Reject oversized ingestion requests before JSON parsing."""
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                exceeds_limit = int(content_length) > MAX_REQUEST_BYTES
            except ValueError:
                exceeds_limit = True
            if exceeds_limit:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "request body is too large"},
                )
        return await call_next(request)

    if runtime_settings.env.lower() in {"development", "dev", "local", "test"}:
        app.include_router(build_ingestion_router(make_session_factory(engine)))

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
