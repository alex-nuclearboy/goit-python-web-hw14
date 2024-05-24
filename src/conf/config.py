"""
Configuration Settings Module
-----------------------------

This module uses Pydantic's BaseSettings to define and validate configuration
settings for the application, ensuring that environment variables are correctly
cast to appropriate Python data types. It facilitates the loading of these
variables from a .env file.

The Settings class encapsulates essential configurations needed throughout the
application, including database connections, email service settings, and cloud
storage options.

The settings instance is initialized at the module level, providing easy
access to configuration throughout the application.

Usage
.....
Access configuration settings via the `settings` instance:

.. code-block:: python

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

    :param postgres_db: PostgreSQL database name.
    :type postgres_db: str
    :param postgres_user: PostgreSQL user name.
    :type postgres_user: str
    :param postgres_password: PostgreSQL user password.
    :type postgres_password: str
    :param postgres_host: Hostname for the PostgreSQL database, \
                          defaults to 'localhost'.
    :type postgres_host: str
    :param postgres_port: Port number for the PostgreSQL database, \
                          defaults to 5432.
    :type postgres_port: int
    :param sqlalchemy_database_url: Full database URL for SQLAlchemy.
    :type sqlalchemy_database_url: str
    :param secret_key: Secret key used for cryptographic operations.
    :type secret_key: str
    :param algorithm: Algorithm used for JWT encoding and decoding.
    :type algorithm: str
    :param mail_username: Username for the mail service.
    :type mail_username: str
    :param mail_password: Password for the mail service.
    :type mail_password: str
    :param mail_from: Sender email address.
    :type mail_from: EmailStr
    :param mail_port: Port number for the mail server.
    :type mail_port: int
    :param mail_server: Hostname of the mail server.
    :type mail_server: str
    :param redis_host: Hostname for Redis server, defaults to 'localhost'.
    :type redis_host: str
    :param redis_port: Port number for the Redis server, defaults to 6379.
    :type redis_port: int
    :param cloudinary_name: Cloudinary cloud name for media storage.
    :type cloudinary_name: str
    :param cloudinary_api_key: API key for Cloudinary.
    :type cloudinary_api_key: str
    :param cloudinary_api_secret: API secret for Cloudinary.
    :type cloudinary_api_secret: str
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

        :param env_file: Path to the .env file from which to load \
                         the environment variables.
        :type env_file: str
        :param env_file_encoding: Encoding of the .env file, \
                                  defaults to 'utf-8'.
        :type env_file_encoding: str
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
