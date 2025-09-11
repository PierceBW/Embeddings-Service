"""add team table and fk

Revision ID: ab96233e7b8f
Revises: f6a3f6d78030
Create Date: 2025-07-24 16:36:40.168437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab96233e7b8f'
down_revision: Union[str, Sequence[str], None] = 'f6a3f6d78030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_TEAM_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    # 1. create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # seed a single default team
    op.execute(
        f"INSERT INTO teams (id, name) VALUES ('{DEFAULT_TEAM_ID}', 'default')"
    )

    # 2. add nullable team_id column to predictions
    op.add_column("predictions", sa.Column("team_id", sa.UUID(), nullable=True))

    # back-fill existing rows with default team
    op.execute(
        f"UPDATE predictions SET team_id = '{DEFAULT_TEAM_ID}'"
    )

    # 3. make the column NOT NULL and add FK
    op.alter_column("predictions", "team_id", nullable=False)
    op.create_foreign_key(
        "fk_predictions_team",
        "predictions",
        "teams",
        ["team_id"],
        ["id"],
    )


def downgrade() -> None:
    # drop FK, column, table (reverse order)
    op.drop_constraint("fk_predictions_team", "predictions", type_="foreignkey")
    op.drop_column("predictions", "team_id")
    op.drop_table("teams")
