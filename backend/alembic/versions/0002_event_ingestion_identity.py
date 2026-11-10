"""Add deterministic event identity for idempotent ingestion."""

import sqlalchemy as sa

from alembic import op

revision = "0002_event_ingestion_identity"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("event_key", sa.String(64), nullable=True))
    op.execute("UPDATE events SET event_key = md5('legacy:' || id::text) WHERE event_key IS NULL")
    op.alter_column("events", "event_key", existing_type=sa.String(64), nullable=False)
    op.create_unique_constraint("uq_events_event_key", "events", ["event_key"])


def downgrade() -> None:
    op.drop_constraint("uq_events_event_key", "events", type_="unique")
    op.drop_column("events", "event_key")
