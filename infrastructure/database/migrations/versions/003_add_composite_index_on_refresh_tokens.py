"""add composite index on refresh tokens
Revision ID: 003_add_composite_index_on_refresh_tokens
Revises: 002_add_user_status_and_password_reset
Create Date: 2026-09-09 16:40:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_add_composite_index_on_refresh_tokens"
down_revision: str | None = "002_add_user_status_and_password_reset"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_refresh_tokens_user_id_is_revoked",
        "refresh_tokens",
        ["user_id", "is_revoked"],
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_user_id_is_revoked", table_name="refresh_tokens")
