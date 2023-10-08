import re

from pydantic import BaseModel, field_validator, EmailStr, model_validator
from pydantic_core import PydanticCustomError


# TODO rename class to `RegisterIn`
class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str

    # TODO rename to `password_confirm`
    password_confirm: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        constraints = [
            len(password) >= 8,
            re.search(r'[0-9]', password) is not None,  # Has a number
            re.search(r'[A-Z]', password) is not None,  # Has an Uppercase letter
            re.search(r'[a-z]', password) is not None,  # Has a Lowercase letter
            re.search(r'[!@#$%^&*()_+{}\[\]:;"\'<>,.?/\\|]', password) is not None  # Has a special char
        ]

        if all(constraints):
            return password
        raise ValueError("Invalid password. Must contain lower and uppercase and special letter up to 8 chars")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise PydanticCustomError(
                "not_matching_passwords",
                "Passwords do not match",
            )
        return self


# TODO rename class to `RegisterOut`
class UserSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


# TODO rename class to `LoginIn`
class UserLogInSchema(BaseModel):
    email: EmailStr
    password: str


# TODO rename class to `RegisterConfirmIn`
class UserVerifySchema(BaseModel):
    email: EmailStr
    totp: str


# TODO rename class to `LoginOut`
class TokenObtainSchema(BaseModel):
    access: str
    refresh: str


# TODO rename class to `RefreshTokenIn`
class TokenRefreshInSchema(BaseModel):
    refresh: str


# TODO rename class to `RefreshTokenOut`
class TokenRefreshOutSchema(BaseModel):
    access: str
