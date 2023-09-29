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

