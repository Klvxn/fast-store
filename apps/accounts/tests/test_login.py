import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager
from ..faker.data import FakeAccount


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
