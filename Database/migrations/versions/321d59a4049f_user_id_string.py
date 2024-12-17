"""user_id>String

Revision ID: 321d59a4049f
Revises: 9835118e95af
Create Date: 2024-12-18 01:59:01.796845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '321d59a4049f'
down_revision: Union[str, None] = '9835118e95af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
