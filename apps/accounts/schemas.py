import re

from pydantic import BaseModel, field_validator, EmailStr, model_validator
from pydantic_core import PydanticCustomError


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    confirm: str

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
        if self.password != self.confirm:
            raise PydanticCustomError(
                "not_matching_passwords",
                "Passwords do not match",
            )
        return self
