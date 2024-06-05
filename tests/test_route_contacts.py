from unittest.mock import MagicMock, patch

from pytest import mark, fixture

from fastapi import status

from src.database.models import User
from src.services.auth import auth_service

from datetime import datetime, timedelta


@fixture()
def token(client, user, session, monkeypatch):
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
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.usefixtures('mock_rate_limit')
def test_get_contact_not_found(client, token):
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
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@mark.usefixtures('mock_rate_limit')
def test_update_contact(client, token):
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
    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"
