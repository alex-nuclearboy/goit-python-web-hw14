from sqlalchemy import Column, Integer, String, Boolean, Date, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    """
    Represents a contact entry in the database,
    storing personal and contact information.

    Attributes:
        id (Integer): The primary key for the contact
                      that is automatically generated.
        first_name (String): The contact's first name, a required field.
        last_name (String): The contact's last name, a required field.
        email (String): The contact's email address, must be unique.
        phone_number (String): The contact's phone number, an optional field.
        birthday (Date): The contact's date of birth, an optional field.
        additional_info (Text): Additional information or notes about
                                the contact, stored as text and is optional.
        created_at (DateTime): The timestamp when the contact was created,
                               defaults to the current time.
        updated_at (DateTime): The timestamp when the contact was last updated,
                               updates automatically on modification.
        user_id (Integer): Foreign key linking to the User model,
                           set to None if not specified.
        user (relationship): A SQLAlchemy ORM relationship that binds
                             the contact to a User, allowing for direct access
                             to the user details.
    """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    email = Column(String(50), unique=True, index=True)
    phone_number = Column(String(15))
    birthday = Column(Date)
    additional_info = Column(Text)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now()
    )
    user_id = Column(
        'user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None
    )
    user = relationship('User', backref="notes")


class User(Base):
    """
    Represents a user entity in the database, storing user authentication
    and identification details.

    Attributes:
        id (Integer): The primary key for the user, automatically generated.
        username (String): The username of the user, optional.
        email (String): The user's unique email address, used for login.
        password (String): The hashed password for the user, required for
                           authentication purposes.
        created_at (DateTime): The timestamp when the user account was created,
                               defaults to the current time.
        updated_at (DateTime): The timestamp when the user information was
                               last updated, updates automatically
                               on modification.
        avatar (String): A URL to the user's avatar image, optional.
        refresh_token (String): A refresh token for the user's session,
                                optional, used in authentication systems
                                to renew access tokens.
        confirmed (Boolean): Indicates whether the user's email address
                             has been confirmed. Defaults to False, and
                             it must be set to True after the user confirms
                             their email.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now()
    )
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
