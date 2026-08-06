"""add youtube_url to projects

Revision ID: 002
Revises: 001
Create Date: 2026-08-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'projects',
        sa.Column('youtube_url', sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('projects', 'youtube_url')