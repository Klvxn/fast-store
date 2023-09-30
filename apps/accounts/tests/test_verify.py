from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from apps.main import app
from config.database import DatabaseManager
from ..error_codes import AccountErrorCodes
from ..faker.data import FakeAccount
from ..services.totp import generate_totp


class TestVerify:
    path = "/accounts/verify"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()

    @classmethod
    def setup_method(cls):
        cls.data = {"email": FakeAccount.user_payload["email"], "totp": "999999"}

    def test_verify_with_empty_payload(self):
        response = self.client.post(url=self.path, json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
    def test_verify_with_invalid_method(self, method: str):
        response = self.client.request(method, url=self.path)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize("missing_key", ["email", "totp"])
    def test_missing_data_fields(self, missing_key: str):
        del self.data[missing_key]
        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert missing_key in response.json()["detail"][0]["loc"]

    @pytest.mark.parametrize("email", ["missing@symbolcom", "user@missingtld.", "@missingusername.com"])
    def test_invalid_email_format(self, email):
        self.data["email"] = email

        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "email" in response.json()["detail"][0]["loc"]

    def test_unavailable_email(self):
        self.data["email"] = "test@invalid.com"
        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == AccountErrorCodes.InvalidVerification

    def test_inactive_user(self):
        # is_verified is True to make sure the inactivity of the account is caught first
        user = FakeAccount.populate_user(is_active=False, is_verified=True)

        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == AccountErrorCodes.InvalidVerification

        FakeAccount.remove_user(user.id)

    def test_already_verified_user(self):
        user = FakeAccount.populate_user(is_verified=True)

        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == AccountErrorCodes.AlreadyVerified

        FakeAccount.remove_user(user.id)

    def test_invalid_totp(self):
        user = FakeAccount.populate_user_with_totp()
        actual_totp = generate_totp(user.totp_secret)
        invalid_totp = "999999"
        if actual_totp == invalid_totp:  # In case they randomly match
            invalid_totp = "999990"

        self.data["totp"] = invalid_totp

        response = self.client.post(self.path, json=self.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == AccountErrorCodes.InvalidTOTP

        FakeAccount.remove_user(user.id)

    @freeze_time(datetime.utcnow())
    def test_successful_verification(self):
        user = FakeAccount.populate_user_with_totp()
        totp_to_send = generate_totp(user.totp_secret)

        self.data["totp"] = totp_to_send

        response = self.client.post(self.path, json=self.data)

        expected = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert expected["email"] == self.data["email"]
        assert expected["is_verified"]
        assert expected["is_active"]
