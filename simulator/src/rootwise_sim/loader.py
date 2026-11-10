"""Load and validate YAML topology and scenario specifications."""

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from .models import ScenarioSpec, TopologySpec

ModelT = TypeVar("ModelT", bound=BaseModel)


def _load_yaml(path: Path, model: type[ModelT]) -> ModelT:
    with path.open(encoding="utf-8") as file:
        return model.model_validate(yaml.safe_load(file))


def load_topology(path: str | Path) -> TopologySpec:
    """Load and validate a topology YAML file."""
    return _load_yaml(Path(path), TopologySpec)


def load_scenario(path: str | Path) -> ScenarioSpec:
    """Load and validate a scenario YAML file."""
    return _load_yaml(Path(path), ScenarioSpec)
