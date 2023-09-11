"""constraint

Revision ID: ee2cd9310f2f
Revises: 9d6e4541d93f
Create Date: 2023-09-11 20:38:51.319941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee2cd9310f2f'
down_revision: Union[str, None] = '9d6e4541d93f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'activations', ['user_id', 'token_id'])
    op.create_unique_constraint(None, 'tokens', ['id'])
    op.create_unique_constraint(None, 'users', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'tokens', type_='unique')
    op.drop_constraint(None, 'activations', type_='unique')
    # ### end Alembic commands ###
