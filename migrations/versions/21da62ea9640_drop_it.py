"""drop it

Revision ID: 21da62ea9640
Revises: 09ecf4ceca27
Create Date: 2025-11-05 19:43:37.114594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21da62ea9640'
down_revision: Union[str, Sequence[str], None] = '09ecf4ceca27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
