from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    """
    Base model for contact information,
    used as a foundation for other contact-related models.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (str): The email address of the contact.
        phone_number (str): The contact's phone number.
        birthday (date): The birthday of the contact.
        additional_info (Optional[str]): Additional information about
                                         the contact, optional.
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
    without additional fields. This model is used for creating new contacts
    where all fields are required.
    """
    pass


class ContactUpdate(BaseModel):
    """
    A model for updating existing contacts. All fields are optional.

    Attributes are identical to ContactBase, but all are optional
    to allow for partial updates.
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

    Attributes:
        id (int): The unique identifier for the contact.
        created_at (datetime): The date and time when the contact was
                               originally created in the system.
        updated_at (datetime): The date and time when the contact information
                               was last updated.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    """
    A model representing the data required to create a user.

    Attributes:
        username (str): The username for the user.
        email (str): The email address of the user.
        password (str): The user's password.
    """
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    A database model for a user, to interface directly with SQLAlchemy.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user information
                               was last updated.
        avatar (str): A URL to the user's avatar.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    A response model that encapsulates the user data along with
    a success message. This model is typically used to send user
    data back to the client after a successful operation.

    Attributes:
        user (UserDb): The user data retrieved from the database.
        detail (str): A message detailing the result of the operation,
                      e.g., "User successfully created".
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    A model representing the authentication tokens including access and
    refresh tokens. This model is used to provide JWTs to the client upon
    successful authentication.

    Attributes:
        access_token (str): The JWT used for accessing protected endpoints.
        refresh_token (str): The JWT used for obtaining a new access token
                             without requiring re-authentication.
        token_type (str): Indicates the type of the tokens, typically "bearer".
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    A model designed to handle incoming email data for requests that
    require user email input. This could include operations like sending
    password reset links or verifying an email address.

    Attributes:
        email (EmailStr): A valid email address provided by the user.
                          The EmailStr type ensures that the email provided
                          conforms to the format of a standard email address.
    """
    email: EmailStr
