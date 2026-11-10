"""Validated request and response schemas for structured log ingestion."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class Severity(StrEnum):
    """Supported normalized severity values."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogRecord(BaseModel):
    """A bounded, validated structured log record."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    service_name: str = Field(
        validation_alias=AliasChoices("service_name", "service"),
        min_length=1,
        max_length=255,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    )
    timestamp: datetime = Field(
        validation_alias=AliasChoices("timestamp", "ts"),
    )
    severity: Severity | str = Field(
        validation_alias=AliasChoices("severity", "level"),
    )
    message: str = Field(min_length=1, max_length=10_000)
    trace_id: str | None = Field(default=None, max_length=255)
    error_signature: str | None = Field(
        default=None,
        validation_alias=AliasChoices("error_signature", "exception"),
        max_length=255,
    )
    source: str = Field(default="log", max_length=100)
    span_id: str | None = Field(default=None, max_length=255)

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        """Require an explicit timezone and normalize all timestamps to UTC."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value.astimezone(UTC)

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value: object) -> str:
        """Normalize common simulator and platform severity spellings."""
        if not isinstance(value, str):
            raise TypeError("severity must be a string")
        normalized = value.strip().upper()
        aliases = {"WARN": "WARNING", "FATAL": "CRITICAL", "ERR": "ERROR"}
        normalized = aliases.get(normalized, normalized)
        if normalized not in {severity.value for severity in Severity}:
            raise ValueError("unsupported severity")
        return normalized


class BatchIngestionRequest(BaseModel):
    """A bounded batch of structured log records."""

    events: list[LogRecord] = Field(min_length=1, max_length=100)


class IngestionResult(BaseModel):
    """Safe summary returned after ingestion."""

    accepted: int
    duplicates: int
    event_ids: list[int]


class BatchIngestionResult(IngestionResult):
    """Batch ingestion summary."""


def canonical_record(record: LogRecord) -> dict[str, Any]:
    """Return canonical JSON-safe data for provenance and identity."""
    return record.model_dump(mode="json", by_alias=False)
