"""
Configuration Settings Module

This module uses Pydantic's BaseSettings to define and validate configuration
settings for the application, ensuring that environment variables are correctly
cast to appropriate Python data types. It facilitates the loading of these
variables from a .env file.

The Settings class encapsulates essential configurations needed throughout the
application, including database connections, email service settings, and cloud
storage options.

The settings instance is initialized at the module level, providing easy
access to configuration throughout the application.

* Usage:
Access configuration settings via the `settings` instance:

```python
from src.conf.config import settings

# Example usage
database_url = settings.sqlalchemy_database_url
"""
from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    """
    A class representing the application's configuration settings, loading from
    environment variables and validating them with Pydantic's BaseSettings.

    Attributes:
        postgres_db (str): PostgreSQL database name.
        postgres_user (str): PostgreSQL user name.
        postgres_password (str): PostgreSQL user password.
        postgres_host (str): Hostname for the PostgreSQL database,
                             defaults to 'localhost'.
        postgres_port (int): Port number for the PostgreSQL database,
                             defaults to 5432.
        sqlalchemy_database_url (str): Full database URL for SQLAlchemy.
        secret_key (str): Secret key used for cryptographic operations.
        algorithm (str): Algorithm used for JWT encoding and decoding.
        mail_username (str): Username for the mail service.
        mail_password (str): Password for the mail service.
        mail_from (EmailStr): Sender email address.
        mail_port (int): Port number for the mail server.
        mail_server (str): Hostname of the mail server.
        redis_host (str): Hostname for Redis server, defaults to 'localhost'.
        redis_port (int): Port number for the Redis server, defaults to 6379.
        cloudinary_name (str): Cloudinary cloud name for media storage.
        cloudinary_api_key (str): API key for Cloudinary.
        cloudinary_api_secret (str): API secret for Cloudinary.
    """
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    sqlalchemy_database_url: str

    secret_key: str
    algorithm: str

    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_port: int
    mail_server: str

    redis_host: str = 'localhost'
    redis_port: int = 6379

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        """
        Configuration settings for the Settings class, defining how environment
        variables are processed and loaded.

        Attributes:
            env_file (str): Path to the .env file from which to load
                            the environment variables.
            env_file_encoding (str): Encoding of the .env file,
                                     defaults to 'utf-8'.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
