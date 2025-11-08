"""empty message

Revision ID: ec8c3153f230
Revises: 609fd7ee3d55, e46cfb8c5ee8
Create Date: 2025-11-08 00:55:25.732239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel   


# revision identifiers, used by Alembic.
revision: str = 'ec8c3153f230'
down_revision: Union[str, Sequence[str], None] = ('609fd7ee3d55', 'e46cfb8c5ee8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
