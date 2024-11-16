"""create token blacklist table

Revision ID: e1c4b7c2742a
Revises: 5ea60ccd7962
Create Date: 2024-11-16 10:51:31.701651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1c4b7c2742a'
down_revision: Union[str, None] = '5ea60ccd7962'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token_blacklist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.Column('blacklisted_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'token')
    )
    op.create_index(op.f('ix_token_blacklist_id'), 'token_blacklist', ['id'], unique=False)
    op.create_index(op.f('ix_token_blacklist_token'), 'token_blacklist', ['token'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_token_blacklist_token'), table_name='token_blacklist')
    op.drop_index(op.f('ix_token_blacklist_id'), table_name='token_blacklist')
    op.drop_table('token_blacklist')
    # ### end Alembic commands ###
