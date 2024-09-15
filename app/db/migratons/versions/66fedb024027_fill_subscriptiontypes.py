"""Fill SubscriptionTypes

Revision ID: 66fedb024027
Revises: d9e3572fdb59
Create Date: 2024-09-12 23:04:13.032983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from config import settings

# revision identifiers, used by Alembic.
revision: str = '66fedb024027'
down_revision: Union[str, None] = 'd9e3572fdb59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    subscription_types_table = sa.table(
        'subscription_types',
        sa.column('name', sa.String),
        sa.column('price', sa.Integer),
        sa.column('duration', sa.Integer),
    )

    op.bulk_insert(subscription_types_table, settings.sub_plan)


def downgrade() -> None:
    op.execute('DELETE FROM subscription_types')
