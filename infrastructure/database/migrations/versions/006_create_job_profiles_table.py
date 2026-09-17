"""create user job profiles table

Revision ID: 006_job_profiles
Revises: 005_workspace_tables
Create Date: 2026-09-17 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "006_job_profiles"
down_revision: str | None = "005_workspace_tables"

branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_job_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_titles", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("primary_skills", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("target_locations", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_remote_only", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("experience_level", sa.String(length=30), nullable=False, server_default="MID"),
        sa.Column("min_salary_usd", sa.Integer(), nullable=True),
        sa.Column("search_status", sa.String(length=30), nullable=False, server_default="ACTIVELY_LOOKING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_user_job_profiles_user_id", "user_job_profiles", ["user_id"], unique=True)
    op.create_index("ix_user_job_profiles_workspace_id", "user_job_profiles", ["workspace_id"])
    op.create_index("ix_user_job_profiles_search_status", "user_job_profiles", ["search_status"])


def downgrade() -> None:
    op.drop_index("ix_user_job_profiles_search_status", table_name="user_job_profiles")
    op.drop_index("ix_user_job_profiles_workspace_id", table_name="user_job_profiles")
    op.drop_index("ix_user_job_profiles_user_id", table_name="user_job_profiles")
    op.drop_table("user_job_profiles")
