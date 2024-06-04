from unittest.mock import MagicMock, patch

from pytest import mark, fixture

from fastapi import status

from src.database.models import User
from src.services.auth import auth_service


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
        response = client.post(
            "/api/contacts",
            json={"first_name": "John",
                  "last_name": "Doe",
                  "email": "john.doe@example.com",
                  "phone_number": "380504238517",
                  "birthday": "2000-01-01",
                  "additional_info": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone_number"] == "380504238517"
        assert data["birthday"] == "2000-01-01"
        assert data["additional_info"] == "Test"
        assert data["id"] == 1
        assert "id" in data
