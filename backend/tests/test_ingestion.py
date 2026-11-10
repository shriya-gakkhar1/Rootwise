from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select

from rootwise.config import Settings
from rootwise.main import create_app
from rootwise.models import Base, Event, Service


def make_client() -> TestClient:
    app = create_app(Settings(database_url="sqlite:///:memory:", env="development"))
    Base.metadata.create_all(app.state.engine)
    return TestClient(app)


def test_single_ingestion_normalizes_and_persists_event() -> None:
    client = make_client()
    response = client.post(
        "/api/v1/events",
        json={
            "service": "order-service",
            "ts": "2026-01-01T00:00:00+05:30",
            "level": "warn",
            "message": "database timeout while loading order",
            "trace_id": "trace-1",
            "exception": "AcquireTimeoutError",
            "stack": "untrusted text",
        },
    )

    assert response.status_code == 201
    assert response.json()["accepted"] == 1
    with client.app.state.engine.connect() as connection:
        event = connection.execute(select(Event)).one()
        service = connection.execute(select(Service)).one()
    assert event.ts == datetime(2025, 12, 31, 18, 30, tzinfo=UTC).replace(tzinfo=None)
    assert event.severity == "WARNING"
    assert event.signature == "AcquireTimeoutError"
    assert event.raw["stack"] == "untrusted text"
    assert service.name == "order-service"


def test_duplicate_single_event_is_idempotent() -> None:
    client = make_client()
    payload = {
        "service_name": "api-gateway",
        "timestamp": "2026-01-01T00:00:00Z",
        "severity": "ERROR",
        "message": "request failed",
    }

    first = client.post("/api/v1/events", json=payload)
    second = client.post("/api/v1/events", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == {"accepted": 1, "duplicates": 0, "event_ids": [1]}
    assert second.json() == {"accepted": 0, "duplicates": 1, "event_ids": []}


def test_batch_ingestion_accepts_duplicates_and_rejects_oversized_batch() -> None:
    client = make_client()
    record = {
        "service": "customer-api",
        "ts": "2026-01-01T00:00:00Z",
        "level": "INFO",
        "message": "request completed",
    }

    response = client.post("/api/v1/events:batch", json={"events": [record, record]})
    too_many = client.post("/api/v1/events:batch", json={"events": [record] * 101})

    assert response.status_code == 201
    assert response.json()["accepted"] == 1
    assert response.json()["duplicates"] == 1
    assert too_many.status_code == 422


def test_invalid_and_oversized_requests_are_safe() -> None:
    client = make_client()
    invalid = client.post(
        "/api/v1/events",
        json={
            "service": "order-service",
            "ts": "2026-01-01T00:00:00",
            "level": "INFO",
            "message": "missing timezone",
        },
    )
    oversized = client.post(
        "/api/v1/events",
        headers={"content-length": str(1_048_577)},
        content=b"{}",
    )

    assert invalid.status_code == 422
    assert "missing timezone" not in invalid.text
    assert oversized.status_code == 413


def test_ingestion_is_not_registered_in_production() -> None:
    app = create_app(
        Settings(database_url="postgresql+psycopg://user:strong-secret@db/rootwise", env="production")
    )
    client = TestClient(app)
    assert client.post("/api/v1/events", json={}).status_code == 404
