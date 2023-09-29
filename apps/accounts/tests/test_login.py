from datetime import datetime

from apps.core.exceptions import ImproperlyConfigured

try:
    from config.settings import ACCESS_TOKEN_EXPIRE_TIME, REFRESH_TOKEN_EXPIRE_TIME
except ImportError:
    raise ImproperlyConfigured("ACCESS_TOKEN_EXPIRE_TIME & REFRESH_TOKEN_EXPIRE_TIME are required to generate JWTs")

from ..services.jwt import Token
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager
from ..error_codes import AccountErrorCodes
from ..faker.data import FakeAccount
from ..models import User


class TestLogin(BaseTestCase):
    path = "/accounts/login"

    @classmethod
    def setup_class(cls):
        DatabaseManager.create_test_database()
        cls.client = TestClient(app)

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()

    @classmethod
    def setup_method(cls):
        cls.db_session = DatabaseManager.session
        cls.data = FakeAccount.user_payload.copy()

    def test_login_with_empty_payload(self):
        response = self.client.post(url=self.path, json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
    def test_login_with_invalid_method(self, method: str):
        response = self.client.request(method, url=self.path)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize("missing_key", ["email", "password"])
    def test_missing_data_fields(self, missing_key: str):
        del self.data[missing_key]
        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("email", ["missing@symbolcom", "user@missingtld.", "@missingusername.com"])
    def test_invalid_email_format(self, email):
        self.data["email"] = email

        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "email" in response.json()["detail"][0]["loc"]

    def test_unavailable_email(self):
        self.data["email"] = "test@invalid.com"
        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidCredentials

    def test_invalid_password(self):
        user = FakeAccount.populate_user(is_verified=True)

        self.data["password"] = "invalid/Pass123"
        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InvalidCredentials

        FakeAccount.remove_user(user.id)

    def test_inactive_user(self):
        user = FakeAccount.populate_user(is_active=False, is_verified=True)

        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.InactiveAccount

        FakeAccount.remove_user(user.id)

    def test_not_verified_user(self):
        user = FakeAccount.populate_user(is_active=True, is_verified=False)

        response = self.client.post(self.path, json=self.data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == AccountErrorCodes.UserNotVerified

        FakeAccount.remove_user(user.id)

    @freeze_time(datetime.utcnow())
    def test_successful_login(self):
        user_created = FakeAccount.populate_user(is_verified=True)
        response = self.client.post(self.path, json=self.data)

        # Retrieve user again to get all the saved data (e.g. last_login)
        refreshed_user = DatabaseManager.session.query(User).get(user_created.id)

        expected = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert "access" in expected
        assert "refresh" in expected
        assert refreshed_user.last_login == datetime.utcnow()

        access_payload = Token.decode(expected["access"])
        refresh_payload = Token.decode(expected["refresh"])

        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
        assert access_payload["sub"] == refresh_payload["sub"] == str(refreshed_user.id)

        current_unix_timestamp = int(datetime.utcnow().timestamp())

        assert access_payload["iat"] == access_payload["nbf"] == current_unix_timestamp
        assert refresh_payload["iat"] == refresh_payload["nbf"] == current_unix_timestamp
        assert access_payload["exp"] == current_unix_timestamp + ACCESS_TOKEN_EXPIRE_TIME.total_seconds()
        assert refresh_payload["exp"] == current_unix_timestamp + REFRESH_TOKEN_EXPIRE_TIME.total_seconds()
