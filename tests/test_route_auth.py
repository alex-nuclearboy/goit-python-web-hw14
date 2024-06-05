"""
Testing Module for User Authentication Operations
-------------------------------------------------

This module provides a suite of synchronous test cases for testing the user
authentication operations of an API using FastAPI and SQLAlchemy. These tests
aim to verify the correct behavior of the API's interaction with a PostgreSQL
database, focusing on user registration, login, and authentication.

The tests use the pytest framework and MagicMock to simulate database
operations and interactions.

**Functions**:

- ``test_create_user``: Verifies user creation and email sending functionality.
- ``test_repeat_create_user``: Ensures proper handling of duplicate user \
                               registration attempts.
- ``test_login_user_not_confirmed``: Checks the behavior when a user attempts \
                                     to log in without email confirmation.
- ``test_login_user``: Tests successful user login after email confirmation.
- ``test_login_wrong_password``: Verifies the login process when an incorrect \
                                 password is provided.
- ``test_login_wrong_email``: Checks the login process when an invalid email \
                              is provided.

**Usage**:

- The test suite can be executed as a standalone script by running the module:

.. code-block:: python

    pytest tests/test_route_auth.py -v
"""

from unittest.mock import MagicMock

from src.database.models import User


def test_create_user(client, user, monkeypatch):
    """
    Verifies user creation and email sending functionality.

    :param client: The test client for making HTTP requests.
    :param user: A dictionary containing user details.
    :param monkeypatch: pytest's monkeypatch fixture for modifying behavior.
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    """
    Ensures proper handling of duplicate user registration attempts.
    """
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    """
    Checks the behavior when a user attempts to log in without \
    email confirmation.
    """
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_login_user(client, session, user):
    """
    Tests successful user login after email confirmation.
    """
    current_user: User = (
        session.query(User).filter(User.email == user.get('email')).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    """
    Verifies the login process when an incorrect password is provided.
    """
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_email(client, user):
    """
    Checks the login process when an invalid email is provided.
    """
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"
