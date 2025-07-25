from app.database import engine
from app.models.user import Base

def init_db():
    Base.metadata.create_all(bind=engine)