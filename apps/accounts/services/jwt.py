from datetime import datetime
from datetime import timedelta
from typing import Optional

from jose import jwt, JWTError

from apps.core.exceptions import ImproperlyConfigured
from config import settings


class Token:
    # Todo : check the security of secret and the way the to distinguish refresh and access tokens
    # Todo: find a way to manage state of tokens so that at each time there is only one access and refresh active
    # TODO: Manage all the abstractions implemented here based on usage of this service class in app

    @staticmethod
    def get_secret_key() -> str:
        secret_key = settings.SECRET_KEY
        if not secret_key:
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

    @staticmethod
    def get_jwt_id() -> str:
        # TODO: Implement jti in order to manage JWTs
        pass

    @classmethod
    def _create_jwt_token(
            cls,
            expires_delta: timedelta,
            token_type: str,
            subject: int,
            issuer: Optional[str] = None
    ) -> str:

        if not issuer:
            issuer = cls.get_issuer()

        payload = {
            "iss": issuer,
            "iat": int(datetime.utcnow().timestamp()),
            "nbf": int(datetime.utcnow().timestamp()),
            "exp": datetime.utcnow() + expires_delta,
            "type": token_type,
            "sub": str(subject)
        }

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

        return cls._create_jwt_token(expires_delta, "access", subject)

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

        return cls._create_jwt_token(expires_delta, "refresh", subject)

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
    def verify_jwt(cls, token: str) -> bool:
        # TODO: manage this function based on prospect usages for authorization and verification
        secret_key = cls.get_secret_key()
        algorithm = cls.get_cryptographic_algorithm()
        issuer = cls.get_issuer()

        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm], issuer=issuer)
            user_id = payload.get("sub")
            if user_id is None or not isinstance(user_id, str):
                return False

            # TODO: Validate token data

        except JWTError:
            return False

        return True
