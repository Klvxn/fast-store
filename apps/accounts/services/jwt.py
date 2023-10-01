from datetime import datetime
from datetime import timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from jose import jwt, JWTError

from apps.core.exceptions import ImproperlyConfigured
from config import settings
from .manager import UserManager
from ..error_codes import AccountErrorCodes
from ..models import User


class Token:
    # Todo : check the security of secret and the way the to distinguish refresh and access tokens
    # Todo: find a way to manage state of tokens so that at each time there is only one access and refresh active
    # TODO: Manage all the abstractions implemented here based on usage of this service class in app
    # TODO: Manage CSRF attacks from JWT

    @staticmethod
    def get_secret_key() -> str:
        try:
            secret_key = settings.SECRET_KEY
        except AttributeError:
            raise ImproperlyConfigured(
                "The SECRET_KEY variable is required to generate tokens"
            )
        if not isinstance(secret_key, str):
            raise TypeError(
                "The SECRET_KEY variable must be of type 'str'"
            )
        return secret_key

    @staticmethod
    def get_cryptographic_algorithm() -> str:
        # TODO: Implement this function based on customer preference for jwt algo
        return "HS256"

    @staticmethod
    def get_issuer() -> str:
        # TODO: Implement issuer based on domain and site url
        pass

    @classmethod
    def get_payload(
            cls,
            subject: int,
            expires_delta: timedelta,
            token_type: str,

    ):
        issuer = cls.get_issuer()
        utc_now = datetime.utcnow()

        payload = {
            "iss": issuer,
            "iat": utc_now,
            "nbf": utc_now,
            "sub": str(subject),
            "exp": utc_now + expires_delta,
            "type": token_type,
        }

        return payload

    @classmethod
    def encode(cls, payload: dict) -> str:

        secret_key = cls.get_secret_key()
        algorithm = cls.get_cryptographic_algorithm()

        return jwt.encode(payload, secret_key, algorithm=algorithm)

    @classmethod
    def create_access_token(
            cls,
            subject: int,
            expires_delta: Optional[timedelta] = None
    ):

        if not expires_delta:
            expires_delta = settings.ACCESS_TOKEN_EXPIRE_TIME

            if not isinstance(expires_delta, timedelta):
                raise TypeError(
                    "Variable ACCESS_TOKEN_EXPIRE_TIME must be of type 'timedelta'"
                )
        payload = cls.get_payload(subject, expires_delta, "access")
        return cls.encode(payload)

    @classmethod
    def create_refresh_token(
            cls,
            subject: int,
            expires_delta: Optional[timedelta] = None
    ):
        if not expires_delta:
            expires_delta = settings.REFRESH_TOKEN_EXPIRE_TIME

            if not isinstance(expires_delta, timedelta):
                raise TypeError(
                    "Variable REFRESH_TOKEN_EXPIRE_TIME must be of type 'timedelta'"
                )

        payload = cls.get_payload(subject, expires_delta, "refresh")
        return cls.encode(payload)

    @classmethod
    def for_user(
            cls,
            user,
            expires_delta: Optional[timedelta] = None
    ):
        access = cls.create_access_token(user.id, expires_delta)
        refresh = cls.create_refresh_token(user.id, expires_delta)

        return {"access": access, "refresh": refresh}

    @classmethod
    def decode(cls, token: str) -> dict:

        secret_key = cls.get_secret_key()
        algorithm = cls.get_cryptographic_algorithm()
        issuer = cls.get_issuer()

        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm], issuer=issuer)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InvalidJWT
            )

        if not (token_type := payload.get("type")) or token_type not in ["access", "refresh"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InvalidTokenType
            )
        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InvalidJWT
            )

        return payload

    @classmethod
    def decode_refresh_token(cls, token: str):
        payload = cls.decode(token)

        if payload["type"] != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InvalidTokenType
            )
        return payload

    @classmethod
    def get_user_from_payload(cls, payload: Dict[str, Any]) -> User:

        user = UserManager.get_user_by_id(int(payload.get("sub")))

        if not user or not user.is_active or not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountErrorCodes.InvalidJWT
            )

        return user
