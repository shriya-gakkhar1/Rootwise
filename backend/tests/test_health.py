import pytest
from fastapi.testclient import TestClient

from rootwise.config import Settings
from rootwise.main import create_app


def test_health_works_with_database() -> None:
    client = TestClient(create_app(Settings(database_url="sqlite:///:memory:")))
    assert client.get("/health").json() == {"status": "ok", "db": True}


def test_production_rejects_development_database_password() -> None:
    with pytest.raises(ValueError, match="development database password"):
        Settings(
            database_url="postgresql+psycopg://rootwise:rootwise@db:5432/rootwise",
            env="production",
        )


def test_production_rejects_loopback_database_host() -> None:
    with pytest.raises(ValueError, match="loopback database host"):
        Settings(
            database_url="postgresql+psycopg://rootwise:strong-secret@localhost:5432/rootwise",
            env="production",
        )
