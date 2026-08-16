# SQLAlchemy setup: the database connection (`engine`), a factory for
# per-request sessions (`SessionLocal`), and the base class every model in
# app/models/ inherits from (`Base`).
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI dependency — yields one DB session per request and always closes
# it afterwards, even if the request handler raises.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
