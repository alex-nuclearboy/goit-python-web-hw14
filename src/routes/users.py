"""
User Profile Management Module

This FastAPI module handles user profile operations, allowing users
to retrieve their profile data and update their avatar images. It integrates
with Cloudinary for image storage and management, ensuring that avatar updates
are handled efficiently and securely.

The module uses rate limiting to prevent abuse of the update functionality.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi import HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
        "/me",
        response_model=UserDb,
        description=(
            "Retrieves the current user's profile information. This endpoint "
            "is available to authenticated users and returns data such as "
            "username, email, and avatar link. Useful for user profile "
            "displays within the application."
        )
)
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user)
) -> UserDb:
    """
    Retrieves the authenticated user's profile data from the database.

    Args:
        current_user (User): The user instance obtained after successful
                             authentication.

    Returns:
        UserDb: A Pydantic model containing the user's profile data such as
        username, email, and avatar URL.
    """
    return current_user


@router.patch(
        '/avatar',
        response_model=UserDb,
        description=(
            "Updates the user's avatar image. This endpoint allows "
            "authenticated users to upload a new avatar image, which will be "
            "stored and managed via Cloudinary. The new avatar URL is then "
            "updated in the user's profile. This endpoint is rate-limited "
            "to 10 requests per minute to prevent abuse."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
) -> UserDb:
    """
    Allows the user to upload a new avatar image, updating their profile with
    the new image URL.

    This endpoint accepts a file upload and updates the avatar in the user's
    profile after uploading the file to Cloudinary. The new avatar URL is then
    saved in the database.

    Args:
        file (UploadFile): The new avatar image to be uploaded.
        current_user (User): The user instance obtained after successful
                             authentication.
        db (Session): The SQLAlchemy session for database interaction.

    Returns:
        UserDb: The updated user profile data including the new avatar URL.

    Raises:
        HTTPException: If there is an issue with the file upload
                       or database update.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    try:
        public_id = f'ContactsApp/{current_user.username}'
        r = cloudinary.uploader.upload(
            file.file, public_id=public_id, overwrite=True
        )
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop='fill', version=r.get('version')
        )

        user = await repository_users.update_avatar(
            current_user.email, src_url, db
        )
        return user
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to update avatar: {str(err)}")
