"""
Database Models Module
----------------------

This module defines the SQLAlchemy ORM models for a Contact Management App.
The models include 'User' for storing user details and 'Contact' for storing
contact information linked to a specific user. These models are used to
interact with the PostgreSQL database, enabling CRUD operations on user and
contact data.

Each model includes fields that are mapped to the database columns, with
appropriate data types and constraints. Relationships are also defined where
necessary to maintain integrity and facilitate easier data retrieval and
manipulation across related records.

**Models**:

- ``Contact``: Represents a contact with personal and communication \
               information.
- ``User``: Represents a user of the application, including authentication \
            details.

The classes use the declarative base class provided by SQLAlchemy to define
database schema and ORM mappings directly in Python code.
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Contact(Base):
    """
    Represents a contact entry in the database,
    storing personal and contact information.

    :param id: The primary key for the contact that is automatically generated.
    :type id: Integer
    :param first_name: The contact's first name, a required field.
    :type first_name: String
    :param last_name: The contact's last name, a required field.
    :type last_name: String
    :param email: The contact's email address, must be unique.
    :type email: String
    :param phone_number: The contact's phone number, an optional field.
    :type phone_number: String
    :param birthday: The contact's date of birth, an optional field.
    :type birthday: Date
    :param additional_info: Additional information or notes about the contact,\
                            stored as text and is optional.
    :type additional_info: Text
    :param created_at: The timestamp when the contact was created, defaults \
                       to the current time.
    :type created_at: DateTime
    :param updated_at: The timestamp when the contact was last updated, \
                       updates automatically on modification.
    :type updated_at: DateTime
    :param user_id: Foreign key linking to the User model, set to None \
                    if not specified.
    :type user_id: Integer
    :param user: A SQLAlchemy ORM relationship that binds the contact \
                 to a User, allowing for direct access to the user details.
    :type user: relationship
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

    :param id: The primary key for the user, automatically generated.
    :type id: Integer
    :param username: The username of the user, optional.
    :type username: String
    :param email: The user's unique email address, used for login.
    :type email: String
    :param password: The hashed password for the user, required for \
                     authentication purposes.
    :type password: String
    :param created_at: The timestamp when the user account was created, \
                       defaults to the current time.
    :type created_at: DateTime
    :param updated_at: The timestamp when the user information was last \
                       updated, updates automatically on modification.
    :type updated_at: DateTime
    :param avatar: A URL to the user's avatar image, optional.
    :type avatar: String
    :param refresh_token: A refresh token for the user's session, optional, \
                          used in authentication systems to renew tokens.
    :type refresh_token: String
    :param confirmed: Indicates whether the user's email address has been \
                      confirmed. Defaults to False, and it must be set \
                      to True after the user confirms their email.
    :type confirmed: Boolean
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
