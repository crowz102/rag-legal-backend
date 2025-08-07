## template for "alembic revision" -- autogen by Alembic
"""${message}

Revision ID: ${uprevision}
Revises: ${down_revision}
Created: ${datetime}
"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = '${uprevision}'
down_revision = '${down_revision}'

def upgrade():
    ${upgrades if upgrades else "pass"}

def downgrade():
    ${downgrades if downgrades else "pass"}