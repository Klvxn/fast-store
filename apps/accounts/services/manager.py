from . import totp
from .hash import Hash
from .. import exceptions
from ..models import User


class UserManager:
    Model = User

    @classmethod
    async def get_user_by_email(cls, email: str):
        return cls.Model.filter(User.email == email).first()

    @classmethod
    async def create(cls, data: dict) -> User:
        if await cls.get_user_by_email(data["email"]):
            raise exceptions.EmailInUse

        data["password"] = Hash.hash_password(data["password"])
        data["totp_secret"] = totp.generate_secret()

        return User.create(**data)

    @classmethod
    async def authenticate(cls, data: dict) -> User:
        user = await cls.get_user_by_email(data["email"])

        if not user or not Hash.verify(data["password"], user.password):
            raise exceptions.InvalidCredentials

        if not user.is_verified:
            raise exceptions.UserNotVerified

        if not user.is_active:
            raise exceptions.InactiveAccount

        return user

    @classmethod
    async def verify(cls, data: dict) -> User:
        user = await cls.get_user_by_email(data["email"])

        if not user or not user.is_active:
            raise exceptions.InvalidVerification

        if user.is_verified:
            raise exceptions.AlreadyVerified

        if not totp.verify_totp(user.totp_secret, data["totp"]):
            raise exceptions.InvalidTOTP

        return User.update(user.id, is_verified=True, totp_secret=None)
