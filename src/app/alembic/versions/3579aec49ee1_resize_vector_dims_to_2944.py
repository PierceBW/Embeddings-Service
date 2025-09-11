"""resize vector dims to 2944

Revision ID: 3579aec49ee1
Revises: ab96233e7b8f
Create Date: 2025-08-12 16:03:33.316881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector  # type: ignore[import-not-found]


# revision identifiers, used by Alembic.
revision: str = '3579aec49ee1'
down_revision: Union[str, Sequence[str], None] = 'ab96233e7b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("predictions", "embedding",
                    type_=Vector(dim=2944), existing_type=Vector(dim=3456))
    op.alter_column("training_samples", "embedding",
                    type_=Vector(dim=2944), existing_type=Vector(dim=3456))

def downgrade():
    op.alter_column("predictions", "embedding",
                    type_=Vector(dim=3456), existing_type=Vector(dim=2944))
    op.alter_column("training_samples", "embedding",
                    type_=Vector(dim=3456), existing_type=Vector(dim=2944))