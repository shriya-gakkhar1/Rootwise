"""Pydantic models for scenario specifications."""

from pydantic import BaseModel, Field


class ServiceSpec(BaseModel):
    name: str
    kind: str


class EdgeSpec(BaseModel):
    from_service: str
    to_service: str
    fan_out_factor: float = Field(default=1.0, gt=0)
    propagation_delay_seconds: int = Field(default=5, ge=0)


class SharedResourceSpec(BaseModel):
    services: list[str] = Field(min_length=2)
    resource: str


class TopologySpec(BaseModel):
    services: list[ServiceSpec] = Field(min_length=1)
    depends_on: list[EdgeSpec]
    shares_resource: list[SharedResourceSpec] = Field(default_factory=list)


class FaultInjection(BaseModel):
    node: str
    description: str
    leak_rate_connections_per_second: float = Field(default=1.0, gt=0)
    pool_size: int = Field(default=100, gt=0)
    utilisation_threshold: float = Field(default=0.8, gt=0, le=1)
    acquire_timeout_ms: float = Field(default=500.0, gt=0)


class DecoyDeploy(BaseModel):
    service: str
    description: str


class GroundTruth(BaseModel):
    cause_node: str
    mechanism: str
    true_onset_seconds: int = Field(ge=0)
    truly_affected_services: list[str]


class ScenarioSpec(BaseModel):
    scenario_id: str
    seed: int
    duration_seconds: int = Field(gt=0)
    start_epoch: str = "2026-01-01T00:00:00+00:00"
    fault_injection: FaultInjection
    decoy_deploy: DecoyDeploy
    ground_truth: GroundTruth
