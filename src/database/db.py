from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

# URL for connecting to the PostgreSQL database
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function for FastAPI to generate database sessions.
    This function creates a new session using SessionLocal, yields it for use,
    and ensures that the session is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint.
    finally:
        db.close()  # Ensure the session is closed after use.
