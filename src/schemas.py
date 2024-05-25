"""
Pydantic Models Module
----------------------

This module contains Pydantic models for user and contact management within
the application. These models enforce validation and typing, ensuring data
integrity when interacting with the database or processing incoming requests.
Each model encapsulates specific fields and validation rules necessary for
various operations: creating, updating, and retrieving users and contacts.

Models:

- ``ContactBase``: Base model for contact fields.
- ``ContactModel``: Inherits from ContactBase for creating new contacts \
                    with required fields.
- ``ContactUpdate``: Allows for partial updates with optional fields.
- ``ContactResponse``: Extends ContactBase to include contact metadata \
                       such as creation and update timestamps.
- ``UserModel``: Defines user creation fields.
- ``UserDb``: Maps to the SQLAlchemy user database model, used for direct \
              interactions with the ORM.
- ``UserResponse``: Provides a structured response for operations involving \
                    user data.
- ``TokenModel``: Represents authentication tokens returned to the user.
- ``RequestEmail``: Used for operations requiring a validated email input.

These models simplify request validation, response serialisation, and
interaction with the ORM, promoting a clean and maintainable codebase.

Models from this module are used in route handlers to validate
incoming data, serialize outgoing data, and interact with the database.

This structured approach ensures that all application data flows are robust
against common data validation issues and are easy to maintain and extend.
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    """
    Base model for contact information,
    used as a foundation for other contact-related models.

    :param first_name: The first name of the contact.
    :type first_name: str
    :param last_name: The last name of the contact.
    :type last_name: str
    :param email: The email address of the contact.
    :type email: str
    :param phone_number: The contact's phone number.
    :type phone_number: str
    :param birthday: The birthday of the contact.
    :type birthday: date
    :param additional_info: Additional information about the contact, optional.
    :type additional_info: Optional[str]
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=50)
    phone_number: str = Field(max_length=15)
    birthday: date
    additional_info: Optional[str] = None


class ContactModel(ContactBase):
    """
    A model representing a contact, extending ContactBase
    without additional fields.

    This model is used for creating new contacts
    where all fields are required.
    """
    pass


class ContactUpdate(BaseModel):
    """
    A model for updating existing contacts. All fields are optional.

    :param first_name: The first name of the contact.
    :type first_name: Optional[str]
    :param last_name: The last name of the contact.
    :type last_name: Optional[str]
    :param email: The email address of the contact.
    :type email: Optional[str]
    :param phone_number: The contact's phone number.
    :type phone_number: Optional[str]
    :param birthday: The birthday of the contact.
    :type birthday: Optional[date]
    :param additional_info: Additional information about the contact.
    :type additional_info: Optional[str]
    """
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=15)
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactResponse(ContactBase):
    """
    A response model for contact information that extends ContactBase
    with additional fields.

    :param id: The unique identifier for the contact.
    :type id: int
    :param created_at: The date and time when the contact was originally \
                       created in the system.
    :type created_at: datetime
    :param updated_at: The date and time when the contact information \
                       was last updated.
    :type updated_at: datetime
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """
        Configuration class for the ContactResponse model.

        :param from_attributes: Indicates that model fields should be \
            populated from attributes rather than dict keys.
        :type from_attributes: bool
        """
        from_attributes = True


class UserModel(BaseModel):
    """
    A model representing the data required to create a user.

    :param username: The username for the user.
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param password: The user's password.
    :type password: str
    """
    username: str = Field(min_length=4, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=15)


class UserDb(BaseModel):
    """
    A database model for a user, to interface directly with SQLAlchemy.

    :param id: The unique identifier for the user.
    :type id: int
    :param username: The username of the user.
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param created_at: The timestamp when the user was created.
    :type created_at: datetime
    :param updated_at: The timestamp when the user information \
                       was last updated.
    :type updated_at: datetime
    :param avatar: A URL to the user's avatar.
    :type avatar: str
    """
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    avatar: str

    class Config:
        """
        Configuration class for the UserDb model.

        :param from_attributes: Indicates that model fields should be \
            populated from attributes rather than dict keys.
        :type from_attributes: bool
        """
        from_attributes = True


class UserResponse(BaseModel):
    """
    A response model that encapsulates the user data along with
    a success message. This model is typically used to send user
    data back to the client after a successful operation.

    :param user: The user data retrieved from the database.
    :type user: UserDb
    :param detail: A message detailing the result of the operation, \
                   e.g., "User successfully created".
    :type detail: str
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    A model representing the authentication tokens including access and
    refresh tokens. This model is used to provide JWTs to the client upon
    successful authentication.

    :param access_token: The JWT used for accessing protected endpoints.
    :type access_token: str
    :param refresh_token: The JWT used for obtaining a new access token \
                          without requiring re-authentication.
    :type refresh_token: str
    :param token_type: Indicates the type of the tokens, typically "bearer".
    :type token_type: str
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    A model designed to handle incoming email data for requests that
    require user email input. This could include operations like sending
    password reset links or verifying an email address.

    :param email: A valid email address provided by the user.
    :type email: EmailStr
    """
    email: EmailStr
