from datetime import datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time
from jose import jwt

from apps.main import app
from config.database import DatabaseManager
from config.settings import SECRET_KEY, REFRESH_TOKEN_EXPIRE_TIME
from ..error_codes import AccountErrorCodes
from ..faker.data import FakeAccount
from ..models import User
from ..services.jwt import Token


# TODO: Add full coverage tests


class TestRefresh:
    path = "/accounts/refresh"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()

    def test_login_with_empty_payload(self):
        response = self.client.post(url=self.path, json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
    def test_login_with_invalid_method(self, method: str):
        response = self.client.request(method, url=self.path)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_missing_data_fields(self):
        data = {"refresh": ""}
        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unavailable_sub_user_token(self):
        data = {"refresh": Token.create_refresh_token(user=User(id=999991223))}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidJWT

    def test_inactive_sub_user_token(self):
        user, token = FakeAccount.get_user_refresh_token(is_active=False, is_verified=True)
        data = {"refresh": token}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidJWT

        FakeAccount.remove_user(user.id)

    def test_not_verified_user_token(self):
        user, token = FakeAccount.get_user_refresh_token(is_active=True)
        data = {"refresh": token}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidJWT

        FakeAccount.remove_user(user.id)

    def test_expired_refresh_token(self):
        with freeze_time(datetime.utcnow() - timedelta(days=2)):
            refresh_token = Token.create_refresh_token(user=User(id=1))
            data = {"refresh": refresh_token}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidJWT

    @pytest.mark.parametrize("missing_payload", ["exp", "sub", "iss", "nbf"])
    def test_refresh_token_missing_payloads(self, missing_payload):
        payloads = Token.get_payload(User(id=123), REFRESH_TOKEN_EXPIRE_TIME, "refresh")
        del payloads[missing_payload]
        data = {"refresh": jwt.encode(payloads, SECRET_KEY, "HS256")}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidJWT

    def test_use_access_token_instead_of_refresh(self):
        user, token = FakeAccount.get_user_access_token(is_verified=True)

        data = {"refresh": token}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidTokenType

        FakeAccount.remove_user(user.id)

    def test_successful_refresh_returns_valid_access_token(self):
        _, token = FakeAccount.get_user_refresh_token(is_verified=True)
        data = {"refresh": token}

        response = self.client.post(self.path, json=data)

        assert response.status_code == status.HTTP_200_OK
        expected = response.json()

        assert "access" in expected

        access_token = expected["access"]

        payload = Token.decode(access_token)
        user = Token.get_user_from_payload(payload)

        assert "type" in payload
        assert payload["type"] == "access"
        assert user.email == FakeAccount.user_payload["email"]
