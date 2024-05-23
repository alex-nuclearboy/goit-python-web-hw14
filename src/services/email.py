"""
This module handles the email sending functionality for the application using
FastAPI-Mail, which provides support for sending emails asynchronously.

It configures the email settings and defines a function to send verification
emails to users during the registration process.
"""

from pathlib import Path

from fastapi import HTTPException

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

# Configuration for FastAPI-Mail,
# using settings from the application configuration.
conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Rest API Application",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email to a user with a link to verify their email address.

    Args:
        email (EmailStr): The email address of the recipient.
        username (str): The username of the recipient, used for
                        personalizing the email.
        host (str): The base URL of the host, used to create the link
                    for email verification.

    Raises:
        HTTPException: An error occurs if the email could not be sent due to
                       server or configuration issues.
    """
    try:
        # Generate a verification token for the email
        token_verification = auth_service.create_email_token({"sub": email})
        # Prepare the email message with a template
        message = MessageSchema(
            subject="Confirm Your Email",
            recipients=[email],  # List of recipients
            template_body={
                "host": str(host),
                "username": username,
                "token": token_verification
            },
            subtype=MessageType.html
        )

        # Send the email using the configured FastMail instance
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(f"Failed to send email: {err}")
        raise HTTPException(status_code=500, detail="Email could not be sent.")


async def send_reset_email(email: EmailStr, username: str, host: str):
    """
    Sends a password reset email to a specified user.

    This function generates a token for password resetting and sends an email
    containing a token that the user can use to verify their identity and
    reset their password through a specified interface, such as Swagger.

    Args:
        email (EmailStr): The email address of the user who requested
                          a password reset.
        username (str): The username of the user to whom the email
                        will be addressed.
        host (str): The base URL of the server where the password reset
                    can be processed.

    Raises:
        HTTPException: An error occurs if the email could not be sent due to
                       server or configuration issues.
    """
    try:
        token_verification = auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={
                "host": str(host),
                "username": username,
                "token": token_verification
            },
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message,
                              template_name="reset_password_email.html")
    except ConnectionErrors as err:
        print(f"Failed to send email: {err}")
        raise HTTPException(status_code=500, detail="Email could not be sent.")
