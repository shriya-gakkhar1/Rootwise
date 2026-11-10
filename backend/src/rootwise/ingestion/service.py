"""Normalization and persistence services for structured logs."""

import hashlib
import json
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from rootwise.models import Event, Service

from .schemas import LogRecord, canonical_record


def event_key(record: LogRecord) -> str:
    """Build a deterministic identity from event fields, excluding arrival time."""
    identity = {
        "service_name": record.service_name,
        "timestamp": record.timestamp.isoformat(),
        "severity": str(record.severity),
        "message": record.message,
        "trace_id": record.trace_id,
        "error_signature": record.error_signature,
        "source": record.source,
        "span_id": record.span_id,
    }
    return hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def resolve_service(session: Session, service_name: str) -> Service:
    """Resolve or register a service with conservative ingestion defaults."""
    service = session.scalar(select(Service).where(Service.name == service_name))
    if service is not None:
        return service
    service = Service(
        name=service_name,
        kind="unknown",
        owner="ingestion",
        slo_target=0.0,
        criticality="unknown",
    )
    session.add(service)
    session.flush()
    return service


def ingest_records(session: Session, records: list[LogRecord]) -> tuple[list[int], int]:
    """Persist normalized records and return accepted IDs and duplicate count."""
    accepted_ids: list[int] = []
    duplicates = 0
    ingest_time = datetime.now(UTC)
    for record in records:
        key = event_key(record)
        existing = session.scalar(select(Event).where(Event.event_key == key))
        if existing is not None:
            duplicates += 1
            continue
        service = resolve_service(session, record.service_name)
        event = Event(
            ts=record.timestamp,
            service_id=service.id,
            source=record.source,
            severity=str(record.severity),
            raw=canonical_record(record),
            signature=record.error_signature,
            trace_id=record.trace_id,
            span_id=record.span_id,
            ingest_ts=ingest_time,
            event_key=key,
        )
        session.add(event)
        session.flush()
        accepted_ids.append(event.id)
    return accepted_ids, duplicates
