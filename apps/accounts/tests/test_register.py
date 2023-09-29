import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.main import app
from config.database import DatabaseManager
from ..models import User
from ..services.hash import Hash


class TestRegister:
    path = "/accounts/register"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()

    @classmethod
    def setup_method(cls):
        cls.db_session = DatabaseManager.session

    @pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
    def test_router_via_not_allowed_methods(self, method: str):
        response = self.client.request(method, self.path)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_empty_body(self):
        response = self.client.post(self.path, json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("missing_key", ["email", "password", "confirm"])
    def test_missing_data_fields(self, missing_key: str):
        data = {"email": "test@user.com", "password": "testpass", "confirm": "testpass"}
        del data[missing_key]
        response = self.client.post(self.path, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_email(self):
        # TODO: Use parametrize
        data = {"email": "invalid.com", "password": "testpass", "confirm": "testpass"}
        response = self.client.post(self.path, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("password", ["inv/P1", "test/pass12", "TEST/PASS12", "testPass123", "test/Pass"])
    def test_invalid_password(self, password):
        data = {"email": "test@user.com", "password": password, "confirm": password}
        response = self.client.post(self.path, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_not_matching_passwords(self):
        data = {"email": "test@user.com", "password": "testpass", "confirm": "notmatching"}
        response = self.client.post(self.path, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_existing_user(self):
        user = User.create(email="test@test.com", password="testpass123")

        data = {"email": user.email, "password": "test/Pass123", "confirm": "test/Pass123"}
        response = self.client.post(self.path, json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_successful_signup(self):
        data = {"email": "test@user.com", "password": "test/Pass123", "confirm": "test/Pass123"}
        response = self.client.post(self.path, json=data)

        expected = response.json()
        user = User.filter(User.email == data["email"]).first()

        assert response.status_code == status.HTTP_201_CREATED
        assert expected["is_active"]
        assert not expected["is_verified"]
        assert expected["email"] == data["email"]

        assert user is not None
        assert Hash.verify(data["password"], user.password)
        assert user.is_active
        assert not user.is_verified
        assert user.totp_secret is not None
