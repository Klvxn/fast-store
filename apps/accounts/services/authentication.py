from fastapi import HTTPException, status

from ..models import User
from ..services.hash import Hash


def authenticate(email: str, password: str) -> User:
    user = User.filter(User.email == email).first()
    if not user or not Hash.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong Email or password"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not verified"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is banned"
        )
    return user
