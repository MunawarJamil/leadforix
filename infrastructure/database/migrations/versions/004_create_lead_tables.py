"""create lead tables

Revision ID: 004_lead_tables
Revises : 003_refresh_tokens_idx
Create Date: 2026-09-13 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "004_lead_tables"
down_revision: str | None = "003_refresh_tokens_idx"

branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable PostgreSQL trigram extension for fuzzy matching
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.create_table(
        "leads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("is_remote", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("salary_info", sa.String(length=255), nullable=True),
        sa.Column("match_score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("matched_skills", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("raw_metadata", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # Standard B-tree indexes
    op.create_index("ix_leads_company_name", "leads", ["company_name"])
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_match_score", "leads", ["match_score"])
    op.create_index("ix_leads_source_source_id", "leads", ["source", "source_id"], unique=True)
    op.create_index("ix_leads_status_match_score", "leads", ["status", "match_score"])

    # Trigram GIN index for fast company similarity matching
    op.execute("CREATE INDEX IF NOT EXISTS ix_leads_company_name_trgm ON leads USING gin (company_name gin_trgm_ops);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_leads_company_name_trgm;")
    op.drop_index("ix_leads_status_match_score", table_name="leads")
    op.drop_index("ix_leads_source_source_id", table_name="leads")
    op.drop_index("ix_leads_match_score", table_name="leads")
    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_company_name", table_name="leads")
    op.drop_table("leads")
