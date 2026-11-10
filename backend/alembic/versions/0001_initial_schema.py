"""Create the initial RootWise schema."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("services", sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(255), nullable=False, unique=True), sa.Column("kind", sa.String(100), nullable=False), sa.Column("owner", sa.String(255), nullable=False), sa.Column("slo_target", sa.Float, nullable=False), sa.Column("criticality", sa.String(50), nullable=False))
    op.create_table("dependencies", sa.Column("id", sa.Integer, primary_key=True), sa.Column("from_service", sa.Integer, nullable=False), sa.Column("to_service", sa.Integer, nullable=False), sa.Column("kind", sa.String(100), nullable=False), sa.Column("timeout_ms", sa.Integer, nullable=False), sa.Column("retries", sa.Integer, nullable=False), sa.Column("source", sa.String(100), nullable=False), sa.Column("confidence", sa.Float, nullable=False))
    op.create_table("events", sa.Column("id", sa.Integer, primary_key=True), sa.Column("ts", sa.DateTime(timezone=True), nullable=False), sa.Column("service_id", sa.Integer, nullable=False), sa.Column("source", sa.String(100), nullable=False), sa.Column("severity", sa.String(50), nullable=False), sa.Column("raw", postgresql.JSONB, nullable=False), sa.Column("template_id", sa.String(255)), sa.Column("signature", sa.String(255)), sa.Column("trace_id", sa.String(255)), sa.Column("span_id", sa.String(255)), sa.Column("ingest_ts", sa.DateTime(timezone=True), nullable=False))
    op.create_table("metrics", sa.Column("ts", sa.DateTime(timezone=True), primary_key=True), sa.Column("service_id", sa.Integer, primary_key=True), sa.Column("metric_name", sa.String(255), primary_key=True), sa.Column("value", sa.Float, nullable=False))
    op.create_table("incidents", sa.Column("id", sa.Integer, primary_key=True), sa.Column("status", sa.String(50), nullable=False), sa.Column("opened_ts", sa.DateTime(timezone=True), nullable=False), sa.Column("closed_ts", sa.DateTime(timezone=True)), sa.Column("severity", sa.String(50), nullable=False), sa.Column("scenario_run_id", sa.String(255)))
    op.create_table("audit_log", sa.Column("id", sa.Integer, primary_key=True), sa.Column("ts", sa.DateTime(timezone=True), nullable=False), sa.Column("actor", sa.String(255), nullable=False), sa.Column("action", sa.String(255), nullable=False), sa.Column("target", sa.String(255), nullable=False), sa.Column("payload_hash", sa.String(255), nullable=False))


def downgrade() -> None:
    for table in ("audit_log", "incidents", "metrics", "events", "dependencies", "services"):
        op.drop_table(table)
