"""SQLAlchemy models for the initial RootWise evidence schema."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    slo_target: Mapped[float] = mapped_column(Float, nullable=False)
    criticality: Mapped[str] = mapped_column(String(50), nullable=False)


class Dependency(Base):
    __tablename__ = "dependencies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_service: Mapped[int] = mapped_column(Integer, nullable=False)
    to_service: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    retries: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    service_id: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    raw: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    template_id: Mapped[str | None] = mapped_column(String(255))
    signature: Mapped[str | None] = mapped_column(String(255))
    trace_id: Mapped[str | None] = mapped_column(String(255))
    span_id: Mapped[str | None] = mapped_column(String(255))
    ingest_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)


class Metric(Base):
    __tablename__ = "metrics"
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    service_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metric_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    opened_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    scenario_run_id: Mapped[str | None] = mapped_column(String(255))


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(255), nullable=False)
