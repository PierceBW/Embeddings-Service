"""add explained_at to predictions

Revision ID: f6a3f6d78030
Revises: 95e7a518e4b7
Create Date: 2025-07-21 15:49:40.935759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a3f6d78030'
down_revision: Union[str, Sequence[str], None] = '95e7a518e4b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema: add explained_at timestamp to predictions."""
    with op.batch_alter_table("predictions") as batch:
        batch.add_column(
            sa.Column("explained_at", sa.DateTime(timezone=True), nullable=True)
        )

def downgrade() -> None:
    """Downgrade schema: drop explained_at column."""
    with op.batch_alter_table("predictions") as batch:
        batch.drop_column("explained_at")
