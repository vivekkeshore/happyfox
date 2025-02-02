"""create gmail message table

Revision ID: bd6d29cb32aa
Revises: 
Create Date: 2024-10-24 01:08:11.291286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bd6d29cb32aa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE SCHEMA IF NOT EXISTS gmail")
    op.create_table('message',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('message_id', sa.String(length=32), nullable=False),
    sa.Column('thread_id', sa.String(length=32), nullable=False),
    sa.Column('from_address', sa.String(length=256), nullable=False),
    sa.Column('to', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('cc', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('bcc', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('received_at', sa.DateTime(), nullable=False),
    sa.Column('subject', sa.String(length=1024), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_id'),
    schema='gmail'
    )
    op.create_index('idx_message_from_address', 'message', ['from_address'], unique=False, schema='gmail')
    op.create_index('idx_message_message_id', 'message', ['message_id'], unique=True, schema='gmail')
    op.create_index('idx_message_subject', 'message', ['subject'], unique=False, schema='gmail')
    op.create_index('idx_message_thread_id', 'message', ['thread_id'], unique=False, schema='gmail')
    op.create_index(op.f('ix_gmail_message_id'), 'message', ['id'], unique=False, schema='gmail')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gmail_message_id'), table_name='message', schema='gmail')
    op.drop_index('idx_message_thread_id', table_name='message', schema='gmail')
    op.drop_index('idx_message_subject', table_name='message', schema='gmail')
    op.drop_index('idx_message_message_id', table_name='message', schema='gmail')
    op.drop_index('idx_message_from_address', table_name='message', schema='gmail')
    op.drop_table('message', schema='gmail')
    op.execute("DROP SCHEMA IF EXISTS gmail CASCADE")
    # ### end Alembic commands ###
