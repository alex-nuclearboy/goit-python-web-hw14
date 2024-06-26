"""
User Management Operations Module
---------------------------------

This module provides asynchronous operations for managing user data within
a database environment. It handles operations such as creating new users,
fetching users by email, updating user authentication tokens, confirming user
emails, and updating user avatars. The functions make extensive use of
SQLAlchemy sessions for database interactions, ensuring transactions are
handled efficiently and safely.

Functions:

- ``get_user_by_email``: Fetch a user from the database by their email \
                         address.
- ``create_user``: Create a new user in the database and optionally assign \
                   a Gravatar image as the avatar.
- ``update_token``: Update or clear the refresh token associated with a user.
- ``confirm_email``: Confirm a user's email address and update the database \
                     to reflect this change.
- ``update_avatar``: Update a user's avatar image URL in the database.

The operations are designed to be used with FastAPI as dependencies within
route handlers, allowing for seamless integration into web applications
requiring user management.
"""

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieve a user by their email address from the database.

    :param email: The email address of the user to retrieve.
    :type email: str
    :param db: The SQLAlchemy session for database interaction.
    :type db: Session
    :return: The user object if found, otherwise None.
    :rtype: User
    """
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as err:
        print(f"Error retrieving user by email {email}: {err}")
        return None


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user in the database and fetch a Gravatar image if available.

    :param body: The user data transfer object containing user details.
    :type body: UserModel
    :param db: The SQLAlchemy session for database interaction.
    :type db: Session
    :return: The newly created user object with all details.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user in the database.

    :param user: The user object whose token is to be updated.
    :type user: User
    :param token: The new refresh token to be saved. \
                  If None, it will clear the existing token.
    :type token: str | None
    :param db: The SQLAlchemy session for database interaction.
    :type db: Session
    :return: None
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    """
    Confirm the user's email address in the database. This function sets the
    'confirmed' status of the user to True, indicating that the user has
    verified their email address.

    :param email: The email address of the user whose email confirmation \
                  status needs to be updated.
    :type email: str
    :param db: The SQLAlchemy session for database interaction.
    :type db: Session
    :return: None
    :rtype: None
    :raises ValueError: If the user with the given email is not found.
    :raises Exception: If any other error occurs during the operation.
    """
    try:
        user = await get_user_by_email(email, db)
        if user is None:
            raise ValueError(f"User with email {email} not found.")
        user.confirmed = True
        db.commit()
    except Exception as err:
        db.rollback()
        raise err


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar URL for a specific user in the database. This function
    sets the 'avatar' field of the user to the new URL provided, which points
    to the location of the updated image.

    :param email: The email address of the user whose avatar is being updated.
    :type email: str
    :param url: The new URL pointing to the avatar image.
    :type url: str
    :param db: The SQLAlchemy session for database interaction.
    :type db: Session
    :return: The updated user object after changing the avatar.
    :rtype: User
    :raises ValueError: If the user with the given email is not found.
    :raises Exception: If any other error occurs during the operation.
    """
    try:
        user = await get_user_by_email(email, db)
        if user is None:
            raise ValueError(f"User with email {email} not found.")
        user.avatar = url
        db.commit()
        return user
    except Exception as err:
        db.rollback()
        raise err
