"""add cancel_policy

Revision ID: 420b10941274
Revises: 812afccba8a6
Create Date: 2025-12-08 20:14:08.099831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '420b10941274'
down_revision: Union[str, None] = '812afccba8a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cancel_policy column to property table"""
    op.add_column(
        'property',
        sa.Column('cancel_policy', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Remove cancel_policy column"""
    op.drop_column('property', 'cancel_policy')
