"""Evaluation record models."""

from typing import Any

from pydantic import BaseModel


class RunRecord(BaseModel):
    scenario_id: str
    seed: int
    system_variant: str
    degradation_config: dict[str, Any]
    results: dict[str, Any]
