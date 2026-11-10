"""Local-development API routes for structured log ingestion."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .schemas import BatchIngestionRequest, BatchIngestionResult, IngestionResult, LogRecord
from .service import ingest_records


def build_ingestion_router(session_factory: Callable[[], Session]) -> APIRouter:
    """Build ingestion routes with an application-owned session factory."""
    router = APIRouter(prefix="/api/v1/events", tags=["ingestion"])

    def get_session() -> Session:
        with session_factory() as session:
            yield session

    @router.post("", response_model=IngestionResult, status_code=status.HTTP_201_CREATED)
    def ingest_event(
        record: LogRecord,
        session: Annotated[Session, Depends(get_session)],
    ) -> IngestionResult:
        """Validate and persist one structured log event."""
        try:
            event_ids, duplicates = ingest_records(session, [record])
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="event ingestion is temporarily unavailable",
            ) from None
        return IngestionResult(
            accepted=len(event_ids),
            duplicates=duplicates,
            event_ids=event_ids,
        )

    @router.post(":batch", response_model=BatchIngestionResult, status_code=status.HTTP_201_CREATED)
    def ingest_batch(
        payload: BatchIngestionRequest,
        session: Annotated[Session, Depends(get_session)],
    ) -> BatchIngestionResult:
        """Validate and persist a bounded batch of structured log events."""
        try:
            event_ids, duplicates = ingest_records(session, payload.events)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="event ingestion is temporarily unavailable",
            ) from None
        return BatchIngestionResult(
            accepted=len(event_ids),
            duplicates=duplicates,
            event_ids=event_ids,
        )

    return router
