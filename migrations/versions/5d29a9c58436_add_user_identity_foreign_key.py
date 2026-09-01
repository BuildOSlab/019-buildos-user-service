"""add user foreign keys

Revision ID: 5d29a9c58436
Revises: bed7baddfe96
Create Date: 2026-09-01
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d29a9c58436"
down_revision: str | None = "bed7baddfe96"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add foreign keys from user-owned tables to users.id."""
    op.create_foreign_key(
        "fk_user_identities_user_id",
        "user_identities",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_user_organizations_user_id",
        "user_organizations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_user_profiles_user_id",
        "user_profiles",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_user_preferences_user_id",
        "user_preferences",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_user_status_history_user_id",
        "user_status_history",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_user_role_references_user_id",
        "user_role_references",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Remove foreign keys from user-owned tables."""
    op.drop_constraint(
        "fk_user_role_references_user_id",
        "user_role_references",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_user_status_history_user_id",
        "user_status_history",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_user_preferences_user_id",
        "user_preferences",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_user_profiles_user_id",
        "user_profiles",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_user_organizations_user_id",
        "user_organizations",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_user_identities_user_id",
        "user_identities",
        type_="foreignkey",
    )
