from datetime import datetime

from fastapi import HTTPException, status

from . import totp
from .hash import Hash
from ..error_codes import AccountErrorCodes
from ..models import User


# TODO rename this class to `OAuthService`
class UserManager:
    Model = User

    @classmethod
    def get_user_by_email(cls, email: str):
        return cls.Model.filter(cls.Model.email == email).first()

    @classmethod
    def get_user_by_id(cls, user_id: int):
        return cls.Model.filter(cls.Model.id == user_id).first()

    @classmethod
    def update_last_login(cls, user_id: int):
        User.update(user_id, last_login=datetime.utcnow())

    @classmethod
    def create_user(cls, data: dict) -> User:
        if cls.get_user_by_email(data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AccountErrorCodes.EmailInUse
            )

        data["password"] = Hash.hash_password(data["password"])
        data["totp_secret"] = totp.generate_secret()

        return User.create(**data)

    @classmethod
    def authenticate(cls, data: dict) -> User:
        user = cls.get_user_by_email(data["email"])

        if not user or not Hash.verify(data["password"], user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InvalidCredentials
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.UserNotVerified
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InactiveAccount
            )

        cls.update_last_login(user.id)
        return user

    @classmethod
    def verify(cls, data: dict) -> User:
        user = cls.get_user_by_email(data["email"])

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AccountErrorCodes.InvalidVerification
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AccountErrorCodes.AlreadyVerified
            )

        if not totp.verify_totp(user.totp_secret, data["totp"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AccountErrorCodes.InvalidTOTP
            )

        return User.update(user.id, is_verified=True, totp_secret=None)
