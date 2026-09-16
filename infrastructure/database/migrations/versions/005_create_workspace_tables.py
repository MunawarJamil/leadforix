"""create workspace and membership tables

Revision ID: 005_workspace_tables
Revises: 004_lead_tables
Create Date: 2026-09-16 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "005_workspace_tables"
down_revision: str | None = "004_lead_tables"

branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create 'workspaces' table
    op.create_table(
        "workspaces",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("tenant_type", sa.String(length=30), nullable=False, server_default="JOB_SEEKER"),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_workspaces_slug", "workspaces", ["slug"], unique=True)
    op.create_index("ix_workspaces_tenant_type", "workspaces", ["tenant_type"])
    op.create_index("ix_workspaces_owner_id", "workspaces", ["owner_id"])

    # 2. Create 'workspace_members' table
    op.create_table(
        "workspace_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="MEMBER"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member_workspace_user"),
    )
    op.create_index("ix_workspace_members_workspace_id", "workspace_members", ["workspace_id"])
    op.create_index("ix_workspace_members_user_id", "workspace_members", ["user_id"])

    # 3. Add 'default_workspace_id' to 'users' table
    op.add_column("users", sa.Column("default_workspace_id", UUID(as_uuid=True), nullable=True))
    op.create_index("ix_users_default_workspace_id", "users", ["default_workspace_id"])


def downgrade() -> None:
    # 1. Revert 'users' column
    op.drop_index("ix_users_default_workspace_id", table_name="users")
    op.drop_column("users", "default_workspace_id")

    # 2. Drop 'workspace_members' table
    op.drop_index("ix_workspace_members_user_id", table_name="workspace_members")
    op.drop_index("ix_workspace_members_workspace_id", table_name="workspace_members")
    op.drop_table("workspace_members")

    # 3. Drop 'workspaces' table
    op.drop_index("ix_workspaces_owner_id", table_name="workspaces")
    op.drop_index("ix_workspaces_tenant_type", table_name="workspaces")
    op.drop_index("ix_workspaces_slug", table_name="workspaces")
    op.drop_table("workspaces")
