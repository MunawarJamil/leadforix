"""add user status and password reset tables

Revision ID: 002_add_user_status_and_password_reset
Revises: 001_create_auth_tables
Create Date: 2026-09-09 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "002_user_status_pwd_reset"
down_revision: str | None = "001_create_auth_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add 'status' column to 'users' table
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="ACTIVE",
        ),
    )

    # 2. Create 'password_reset_tokens' table
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index(
        "ix_password_reset_tokens_token_hash",
        "password_reset_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_password_reset_tokens_expires_at",
        "password_reset_tokens",
        ["expires_at"],
    )
    op.create_index(
        "ix_password_reset_tokens_is_used",
        "password_reset_tokens",
        ["is_used"],
    )


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
    op.drop_column("users", "status")
