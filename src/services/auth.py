"""
Authentication and Authorisation Module
---------------------------------------

This module provides a comprehensive suite of functionalities for handling
authentication and authorisation in a Contact Management application.
It encapsulates the operations needed to handle user authentication, including
password hashing, token generation and validation, and user retrieval based
on JWT tokens.

The module uses the Pydantic library for settings management, the Passlib
library for password hashing, and the python-jose library for JWT operations,
integrating seamlessly with FastAPI's dependency injection system to ensure
secure and scalable user authentication.

**Classes**:

- ``Auth``: The main class that provides methods for user authentication \
            and token handling.
"""

from typing import Optional
from datetime import datetime, timedelta, timezone

import pickle
import redis

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.models import User
from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    # Redis instance for storing refresh tokens or other temporary data.
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(
            self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Verifies a given plaintext password against the hashed password.

        :param plain_password: The plaintext password to verify.
        :type plain_password: str
        :param hashed_password: The hash of the password to compare against.
        :type hashed_password: str
        :return: True if the password is correct, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Generates a password hash from a plaintext password.

        :param password: The plaintext password to hash.
        :type password: str
        :return: The hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(
            self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates a JWT access token with an optional expiry delta.

        :param data: The data to encode in the token, typically containing \
                     the user's identity.
        :type data: dict
        :param expires_delta: The number of seconds until the token expires.
        :type expires_delta: Optional[float]
        :return: The encoded JWT access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY,
                                          algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(
            self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates a JWT refresh token used to obtain new access tokens.

        :param data: The data to encode in the token.
        :type data: dict
        :param expires_delta: The number of seconds until the token expires.
        :type expires_delta: Optional[float]
        :return: The encoded JWT refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decodes a JWT refresh token and validates its scope.

        :param refresh_token: The refresh token to decode.
        :type refresh_token: str
        :return: The user's email extracted from the token if valid.
        :rtype: str
        :raises HTTPException: If the token is invalid or has the wrong scope.
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme),
                               db: Session = Depends(get_db)) -> User:
        """
        Retrieves the current user from a JWT token.

        :param token: The JWT token to decode.
        :type token: str
        :param db: The database session used to retrieve user data.
        :type db: Session
        :return: The user object retrieved from the database.
        :rtype: User
        :raises HTTPException: If the token is invalid or the user \
                               does not exist.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Decode JWT
            payload = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict) -> str:
        """
        Creates a token for email verification purposes.

        :param data: The data to include in the token, the user's email.
        :type data: dict
        :return: The encoded token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Extracts the user's email address from a verification token.

        :param token: The token from which to extract the email.
        :type token: str
        :return: The email address decoded from the token.
        :rtype: str
        :raises HTTPException: If the token is invalid or cannot be processed.
        """
        try:
            payload = jwt.decode(
                token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid token for email verification")


auth_service = Auth()
