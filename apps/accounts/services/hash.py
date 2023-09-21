from passlib.context import CryptContext


class Hash:
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str):
        return cls.pwd_ctx.hash(password)

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str):
        return cls.pwd_ctx.verify(plain_password, hashed_password)
