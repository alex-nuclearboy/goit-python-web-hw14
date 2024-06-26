"""
Authentication Module
---------------------

This module provides endpoints for user authentication processes, including
signup, login, password reset, and email verification. It uses FastAPI's
dependency injection system to manage authentication states and rate limiting
to secure the endpoints against abuse.

The module integrates with SQLAlchemy for database operations, FastAPI-Mail
for sending emails, and JWT tokens for secure and stateless authentication.
It includes functionalities such as user registration, login, email
confirmation, password reset requests, and actual password reset confirmation
through secure tokens.

All endpoints are protected with rate limiting to prevent abuse and ensure the
service's stability. The module uses dependency injections for database
sessions and current user identification, ensuring that requests are handled
securely and efficiently.

This module uses HTTPBearer as a security scheme to protect endpoints that
require user identification. OAuth2PasswordBearer is used for handling login
data securely.
"""
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email, send_reset_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post(
        "/signup", response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        description=(
            "Registers a new user account. After submitting required "
            "user information, a verification email is sent to the user's  "
            "email address."
        )
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user in the system and send an email verification link.

    :param body: User data (username, email, password).
    :type body: UserModel
    :param background_tasks: Background tasks for email sending.
    :type background_tasks: BackgroundTasks
    :param request: Request object to access headers and other details.
    :type request: Request
    :param db: Database session dependency.
    :type db: Session
    :return: The created user data and a success message.
    :rtype: UserResponse
    :raises HTTPException: 409 Conflict if user already exists.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {
        "user": new_user,
        "detail": (
            "User successfully created. "
            "Check your email for confirmation."
        )
    }


@router.post(
        "/login", response_model=TokenModel,
        description=(
            "Authenticates a user by their email and password, returning "
            "JWT access and refresh tokens if successful. Ensures that only "
            "confirmed emails can log in to enhance security."
        )
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> TokenModel:
    """
    Authenticate a user using email and password, returning JWT access and
    refresh tokens.

    :param body: The form data containing the email and password.
    :type body: OAuth2PasswordRequestForm
    :param db: Database session dependency.
    :type db: Session
    :return: Access and refresh JWT tokens.
    :rtype: TokenModel
    :raises HTTPException: 401 Unauthorized if login details are incorrect \
                           or if the email is not confirmed.
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed"
        )

    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    # Generate JWT
    access_token = (
        await auth_service.create_access_token(data={"sub": user.email})
    )
    refresh_token = (
        await auth_service.create_refresh_token(data={"sub": user.email})
    )
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get(
        '/refresh_token', response_model=TokenModel,
        description=(
            "Allows a user to refresh their session by validating an existing "
            "refresh token and issuing new access and refresh tokens."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> TokenModel:
    """
    Refreshes authentication by validating an existing refresh token and
    issuing new tokens.

    :param credentials: Credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Database session dependency.
    :type db: Session
    :return: New access and refresh JWT tokens.
    :rtype: TokenModel
    :raises HTTPException: 401 Unauthorized if the refresh token \
                           is invalid or expired.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = (
        await auth_service.create_access_token(data={"sub": email})
    )
    refresh_token = (
        await auth_service.create_refresh_token(data={"sub": email})
    )
    await repository_users.update_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get(
        '/confirm_email/{token}',
        description=(
            "Confirms a user's email address using a token sent to the user's "
            "email upon registration. Validates the token and marks the email "
            "as confirmed."
        )
)
async def confirm_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Confirms a user's email address using a token sent during registration.

    :param token: Verification token received by the user.
    :type token: str
    :param db: Database session dependency.
    :type db: Session
    :return: Confirmation message.
    :rtype: dict
    :raises HTTPException: 400 Bad Request if the token is invalid \
                           or the user does not exist.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error"
        )

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirm_email(email, db)
    return {"message": "Email confirmed"}


@router.post(
        '/request_email',
        description=(
            "Allows a user to request a new email verification if they "
            "haven't received the initial confirmation email or the link "
            "has expired."
        )
)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    Sends a new email verification token if the initial token is lost
    or expired.

    :param body: Email of the user requesting a new token.
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending email.
    :type background_tasks: BackgroundTasks
    :param request: Request object to access host details for link generation.
    :type request: Request
    :param db: Database session dependency.
    :type db: Session
    :return: Message indicating email sending status.
    :rtype: dict
    :raises HTTPException: 404 Not Found if no user is associated \
                           with the provided email.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("No account found with this email address. "
                    "Please check your email address or register.")
        )

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )

    return {"message": "Check your email for confirmation."}


@router.post(
        "/password-reset/",
        description=(
            "Initiates a password reset process for a user who has forgotten "
            "their password. A password reset link with a token is sent to "
            "the user's  registered email."
        )
)
async def password_reset_request(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    Sends a password reset link to the user's email if registered
    in the system.

    :param body: Contains the email address for sending the reset link.
    :type body: RequestEmail
    :param background_tasks: Used to handle email sending in the background.
    :type background_tasks: BackgroundTasks
    :param request: Request object to access host details for link generation.
    :type request: Request
    :param db: Database session dependency.
    :type db: Session
    :return: Message indicating if the email was sent or not.
    :rtype: dict
    :raises HTTPException: 404 Not Found if the email does not exist \
                           in the database.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist."
        )

    background_tasks.add_task(
        send_reset_email, user.email, user.username, request.base_url
    )

    return {
        "message": "If your email is registered, "
        "we've sent a link to reset your password."
    }


@router.post(
        "/password-reset/confirm/",
        description=(
            "Allows a user to reset their password using a valid token "
            "received via email. This endpoint confirms the token's validity, "
            "applies the new password, and updates the user's account."
        )
)
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Resets the user's password given a valid token and a new password.

    :param token: The token sent to the user's email for password reset.
    :type token: str
    :param new_password: The new password to set for the user.
    :type new_password: str
    :param db: Database session dependency.
    :type db: Session
    :return: Confirmation message stating the password reset was successful.
    :rtype: dict
    :raises HTTPException: 404 Not Found if the token is invalid or the user \
                           does not exist.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    hashed_password = auth_service.get_password_hash(new_password)
    user.password = hashed_password
    db.commit()
    return {"message": "Your password has been reset successfully."}
