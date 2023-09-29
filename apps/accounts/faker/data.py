from ..models import User
from ..services.manager import UserManager


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
