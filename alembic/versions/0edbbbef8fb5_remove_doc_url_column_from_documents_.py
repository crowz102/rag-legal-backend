"""Remove doc_url column from documents table

Revision ID: 0edbbbef8fb5
Revises: 
Created: 2025-08-05 23:40:00.123456
"""

from alembic import op
import sqlalchemy as sa

revision = '0edbbbef8fb5'
down_revision = None

def upgrade():
    op.drop_column('documents', 'doc_url')

def downgrade():
    op.add_column('documents', sa.Column('doc_url', sa.String(), nullable=False))