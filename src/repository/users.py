"""
User Management Operations Module

This module provides asynchronous operations for managing user data within
a database environment. It handles operations such as creating new users,
fetching users by email, updating user authentication tokens, confirming user
emails, and updating user avatars. The functions make extensive use of
SQLAlchemy sessions for database interactions, ensuring transactions are
handled efficiently and safely.

Functions:
- get_user_by_email: Fetch a user from the database by their email address.
- create_user: Create a new user in the database and optionally assign
               a Gravatar image as the avatar.
- update_token: Update or clear the refresh token associated with a user.
- confirm_email: Confirm a user's email address and update the database
                 to reflect this change.
- update_avatar: Update a user's avatar image URL in the database.

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

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The SQLAlchemy session for database interaction.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user in the database and fetch a Gravatar image if available.

    Args:
        body (UserModel): The user data transfer object containing
                          user details.
        db (Session): The SQLAlchemy session for database interaction.

    Returns:
        User: The newly created user object with all details.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user in the database.

    Args:
        user (User): The user object whose token is to be updated.
        token (str | None): The new refresh token to be saved.
                            If None, it will clear the existing token.
        db (Session): The SQLAlchemy session for database interaction.
    """
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session) -> None:
    """
    Confirm the user's email address in the database. This function sets the
    'confirmed' status of the user to True, indicating that the user has
    verified their email address.

    Args:
        email (str): The email address of the user whose email confirmation
                     status needs to be updated.
        db (Session): The SQLAlchemy session for database interaction.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar URL for a specific user in the database. This function
    sets the 'avatar' field of the user to the new URL provided, which points
    to the location of the updated image.

    Args:
        email (str): The email address of the user whose avatar
                     is being updated.
        url (str): The new URL pointing to the avatar image.
        db (Session): The SQLAlchemy session for database interaction.

    Returns:
        User: The updated user object after changing the avatar.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
