"""
Testing Module for Contact Management Operations
------------------------------------------------

This module provides a suite of synchronous test cases for testing the CRUD
operations and additional functionalities of a Contact Management API
using FastAPI and SQLAlchemy. These tests aim to verify the correct behavior
of the API's interaction with a PostgreSQL database, focusing on creating,
retrieving, updating, deleting contacts, and getting upcoming birthdays.

The tests utilize the pytest framework and MagicMock to simulate database
operations and interactions.

**Fixtures**:

- ``token``: Generates an authentication token for the test client by
  registering and logging in a test user.

**Test Functions**:

- ``test_create_contact``: Verifies the creation of a new contact with a \
                           birthday set to the current date plus 3 days but \
                           with the year set to 2000.
- ``test_get_contact``: Ensures that retrieving an existing contact by ID \
                        works correctly and checks the returned data.
- ``test_get_contact_unauthorised``: Checks the behavior when an unauthorised \
                                     request is made to retrieve a contact.
- ``test_get_contact_not_found``: Ensures that the system returns the correct \
                                  status and message when attempting \
                                  to retrieve a non-existent contact.
- ``test_get_contacts``: Verifies the retrieval of multiple contacts with the \
                         appropriate headers and checks the returned data.
- ``test_get_contacts_unauthorised``: Ensures that unauthorised requests to \
                                      retrieve multiple contacts are handled \
                                      correctly.
- ``test_get_upcoming_birthdays``: Verifies that the system correctly \
                                   identifies contacts with birthdays \
                                   occurring within the next week.
- ``test_update_contact``: Confirms that updating an existing contact's \
                           information works as expected.
- ``test_update_contact_not_found``: Ensures that the system returns the \
                                     correct status and message when \
                                     attempting to update a non-existent \
                                     contact.
- ``test_delete_contact``: Verifies the deletion of an existing contact and \
                           checks the returned data.
- ``test_repeat_delete_contact``: Ensures that the system returns the correct \
                                  status and message when attempting to \
                                  delete a contact that has already been \
                                  deleted.

**Usage**:

- The test suite can be executed as a standalone script by running the module:

.. code-block:: python

    pytest tests/test_route_contacts.py -v
"""

from unittest.mock import MagicMock, patch

from pytest import mark, fixture

from fastapi import status

from src.database.models import User
from src.services.auth import auth_service

from datetime import datetime, timedelta


@fixture()
def token(client, user, session, monkeypatch):
    """
    This fixture registers, confirms, and logs in a test user \
    to generate an authentication token.
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = (
        session.query(User).filter(User.email == user.get('email')).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@mark.usefixtures('mock_rate_limit')
def test_create_contact(client, token):
    """
    Verifies the creation of a new contact with a birthday set to the current \
    date plus 3 days but with the year set to 2000.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=2000)  # Change the year to 2000
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.post(
            "/api/contacts",
            json={"first_name": "John",
                  "last_name": "Doe",
                  "email": "john.doe@example.com",
                  "phone_number": "380504238517",
                  "birthday": birthday_str,
                  "additional_info": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone_number"] == "380504238517"
        assert data["birthday"] == birthday_str
        assert data["additional_info"] == "Test"
        assert data["id"] == 1
        assert "id" in data


@mark.usefixtures('mock_rate_limit')
def test_get_contact(client, token):
    """
    Ensures that retrieving an existing contact by ID works correctly \
    and checks the returned data.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=2000)  # Change the year to 2000
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone_number"] == "380504238517"
        assert data["birthday"] == birthday_str
        assert data["additional_info"] == "Test"
        assert "id" in data


@mark.usefixtures('mock_rate_limit')
def test_get_contact_unauthorised(client):
    """
    Checks the behavior when an unauthorised request \
    is made to retrieve a contact.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.usefixtures('mock_rate_limit')
def test_get_contact_not_found(client, token):
    """
    Ensures that the system returns the correct status and message \
    when attempting to retrieve a non-existent contact.
  """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/10",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


@mark.usefixtures('mock_rate_limit')
def test_get_contacts(client, token):
    """
    Verifies the retrieval of multiple contacts with the appropriate headers \
    and checks the returned data.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=2000)  # Change the year to 2000
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "John"
        assert data[0]["last_name"] == "Doe"
        assert data[0]["email"] == "john.doe@example.com"
        assert data[0]["phone_number"] == "380504238517"
        assert data[0]["birthday"] == birthday_str
        assert data[0]["additional_info"] == "Test"
        assert "id" in data[0]


@mark.usefixtures('mock_rate_limit')
def test_get_contacts_unauthorised(client):
    """
    Ensures that unauthorised requests to retrieve multiple contacts \
    are handled correctly.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.usefixtures('mock_rate_limit')
def test_get_upcoming_birthdays(client, token):
    """
    Verifies that the system correctly identifies contacts with birthdays \
    occurring within the next week.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=2000)  # Change the year to 2000
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.get(
            "/api/contacts/birthdays",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == "John"
        assert data[0]["last_name"] == "Doe"
        assert data[0]["email"] == "john.doe@example.com"
        assert data[0]["phone_number"] == "380504238517"
        assert data[0]["birthday"] == birthday_str
        assert data[0]["additional_info"] == "Test"
        assert "id" in data[0]


@mark.usefixtures('mock_rate_limit')
def test_update_contact(client, token):
    """
    Confirms that updating an existing contact's information works as expected.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=1990)  # Change the year to 1990
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.patch(
            "/api/contacts/1",
            json={"first_name": "Mike",
                  "email": "mike.doe@example.com",
                  "birthday": birthday_str,
                  "additional_info": "Update test"},
            headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["first_name"] == "Mike"
        assert data["email"] == "mike.doe@example.com"
        assert data["birthday"] == birthday_str
        assert data["additional_info"] == "Update test"
        assert "id" in data


@mark.usefixtures('mock_rate_limit')
def test_update_contact_not_found(client, token):
    """
    Ensures that the system returns the correct status and message \
    when attempting to update a non-existent contact.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=1990)  # Change the year to 1990
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.patch(
            "/api/contacts/10",
            json={"first_name": "Mike",
                  "email": "mike.doe@example.com",
                  "birthday": birthday_str,
                  "additional_info": "Update test"},
            headers={"Authorization": f"Bearer {token}"}, )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


@mark.usefixtures('mock_rate_limit')
def test_delete_contact(client, token):
    """
    Verifies the deletion of an existing contact and checks the returned data.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        tmp_day = datetime.now() + timedelta(days=3)  # Current date + 3 days
        birthday = tmp_day.replace(year=1990)  # Change the year to 1990
        birthday_str = birthday.strftime("%Y-%m-%d")
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["first_name"] == "Mike"
        assert data["last_name"] == "Doe"
        assert data["email"] == "mike.doe@example.com"
        assert data["phone_number"] == "380504238517"
        assert data["birthday"] == birthday_str
        assert data["additional_info"] == "Update test"
        assert "id" in data


@mark.usefixtures('mock_rate_limit')
def test_repeat_delete_contact(client, token):
    """
    Ensures that the system returns the correct status and message \
    when attempting to delete a contact that has already been deleted.
    """
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"
