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
            "Registers a new user account. After submitting required user "
            "information, a verification email is sent to the user's email "
            "address. This endpoint is rate-limited to 10 requests per minute "
            "to prevent abuse."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
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
            "confirmed emails can log in to enhance security. "
            "Rate-limited to 10 requests per minute."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
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
            "refresh token and issuing new access and refresh tokens. "
            "This process is rate-limited to 10 requests per minute "
            "to maintain security."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
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
            "as confirmed. Rate-limited to 10 requests per minute to prevent "
            "abuse of the endpoint."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def confirm_email(token: str, db: Session = Depends(get_db)):
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
            "has expired. Rate-limited to 10 requests per minute."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
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
            "the user's  registered email. "
            "Rate-limited to 10 requests per minute."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def password_reset_request(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
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
            "applies the new password, and updates the user's account. "
            "Rate-limited to 10 requests per minute."
        ),
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
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
