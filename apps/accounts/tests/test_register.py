import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager
from ..error_codes import AccountErrorCodes
from ..faker.data import FakeAccount


class OAuthTestBase(BaseTestCase):
    register_endpoint = "/accounts/register/"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestRegister(OAuthTestBase):
    # @classmethod
    # def setup_method(cls):
    #     cls.data = FakeAccount.user_payload.copy()
    #     cls.data["confirm"] = cls.data["password"]

    def test_register_with_email(self):
        """
        Test Register a new user with valid credentials.
        """
        payload = {
            'email': 'admin@test.com',
            'password': 'Test_12345',
            'password_confirm': 'Test_12345'
        }

        # --- request ---
        response = self.client.post(self.register_endpoint, json=payload)
        print(response.content)
        assert response.status_code == status.HTTP_201_CREATED

        # TODO after create a user send a message:
        #  {'detail' : "Confirm email, I send a code to your email at 'user_email'. please check it to confirm the email-address."}

        # --- expected ---

        # TODO now check some fields by checking the data using `OAuthService.get_user()`

        # TODO move the to `OAuthService.get_user()`
        # user = User.filter(User.email == self.data["email"]).first()

        # expected = response.json()

        # TODO don't sent this information after first registration. just show the message to confirm
        # assert expected["is_active"] is False
        # assert expected["is_verified"] is False
        # assert expected["email"] == self.data["email"]
        #
        # assert user is not None
        # assert Hash.verify(self.data["password"], user.password)
        # assert user.is_active
        # assert not user.is_verified
        # assert user.totp_secret is not None

    # TODO test the OTP for validate the user email (after register request)

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    @pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
    def test_router_via_not_allowed_methods(self, method: str):
        response = self.client.request(method, self.register_endpoint)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_empty_body(self):
        response = self.client.post(self.register_endpoint, json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("missing_key", ["email", "password", "confirm"])
    def test_missing_data_fields(self, missing_key: str):
        del self.data[missing_key]
        response = self.client.post(self.register_endpoint, json=self.data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "invalid_email",
        ["missing@symbolcom", "user@missingtld.", "@missingusername.com"]
    )
    def test_invalid_email(self, invalid_email):
        self.data["email"] = invalid_email
        response = self.client.post(self.register_endpoint, json=self.data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "password",
        ["inv/P1", "test/pass12", "TEST/PASS12", "testPass123", "test/Pass"]
    )
    def test_invalid_password(self, password):
        self.data["password"] = self.data["confirm"] = password
        response = self.client.post(self.register_endpoint, json=self.data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_not_matching_passwords(self):
        self.data["confirm"] = "notmatching/Pass123"
        response = self.client.post(self.register_endpoint, json=self.data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_existing_user(self):
        user = FakeAccount.populate_user(is_verified=True)

        response = self.client.post(self.register_endpoint, json=self.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == AccountErrorCodes.EmailInUse

        FakeAccount.remove_user(user.id)
