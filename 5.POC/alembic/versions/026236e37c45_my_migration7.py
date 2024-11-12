"""My migration7

Revision ID: 026236e37c45
Revises: d7094f718d54
Create Date: 2024-06-28 10:54:27.798900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '026236e37c45'
down_revision: Union[str, None] = 'd7094f718d54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patients', sa.Column('dob', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patients', 'dob')
    # ### end Alembic commands ###
