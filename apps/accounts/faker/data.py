# TODO refactor imports: e.g. `from apps.accounts.models import User`
from ..models import User
from ..services.jwt import Token
from ..services.manager import UserManager
from ..services.totp import generate_secret


# TODO use the code in the django project.
class FakeAccount:
    user_payload = {
        "email": "test@test.com",
        "password": "test/Pass123",
    }

    @classmethod
    def populate_user(cls, **kwargs):
        payload = cls.user_payload.copy()
        payload.update(kwargs)
        return UserManager.create_user(payload)

    @classmethod
    def remove_user(cls, user_id):
        User.delete(user_id)

    @classmethod
    def populate_user_with_totp(cls, **kwargs):
        secret_key = generate_secret()
        user = cls.populate_user(totp_secret=secret_key, **kwargs)
        return user

    @classmethod
    def get_user_refresh_token(cls, **kwargs):
        user = cls.populate_user(**kwargs)
        return user, Token.create_refresh_token(user)

    @classmethod
    def get_user_access_token(cls, **kwargs):
        user = cls.populate_user(**kwargs)
        return user, Token.create_access_token(user)
