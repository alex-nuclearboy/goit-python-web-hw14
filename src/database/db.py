"""
Database Connection Module
--------------------------

This module sets up the SQLAlchemy engine and session factory for interacting
with the PostgreSQL database. It configures and provides a sessionmaker
instance that is used throughout the application to handle database sessions
efficiently.

The module uses settings from the application's configuration to establish
the database connection, ensuring that all database operations are centralised
and easily manageable.

**Attributes**:

- ``SQLALCHEMY_DATABASE_URL (str)``: A string representing the complete \
    database connection URL.
- ``engine (Engine)``: SQLAlchemy Engine instance for the database connection.
- ``SessionLocal (sessionmaker)``: Configured sessionmaker that binds \
    to the engine and can be used to create new session objects.

**Functions**:

- ``get_db()``: Generator function that yields a new SQLAlchemy session \
                for each request and closes it once the request is completed.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

# URL for connecting to the PostgreSQL database
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

# Create an engine instance connected to the PostgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Configure a sessionmaker to be used for creating Session instances
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function for FastAPI to generate database sessions dynamically.

    This generator function is designed to be used as a dependency in FastAPI
    routes. It creates a new session from the SessionLocal factory, yields it
    for the duration of the request, and ensures that the session is closed
    after the request is processed. This pattern ensures that database
    resources are managed efficiently, with each request getting a clean
    session, ensuring there are no leftover transactions or uncommitted data.

    :yield: Yields a database session that is scoped to the lifetime \
            of a request.
    :rtype: sqlalchemy.orm.Session
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint for db operations.
    finally:
        db.close()  # Ensure the session is closed after use.
