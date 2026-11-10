import os

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="requires TEST_DATABASE_URL")
def test_initial_migration_applies_to_clean_database() -> None:
    database_url = os.environ["TEST_DATABASE_URL"]
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP SCHEMA public CASCADE")
        connection.exec_driver_sql("CREATE SCHEMA public")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")
    assert set(inspect(engine).get_table_names()) >= {
        "services", "dependencies", "events", "metrics", "incidents", "audit_log"
    }
    assert "event_key" in {column["name"] for column in inspect(engine).get_columns("events")}
