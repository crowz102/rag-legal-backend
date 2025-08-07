import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.document import Base
from alembic import context

target_metadata = Base.metadata