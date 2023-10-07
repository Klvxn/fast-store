from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .error_codes import AccountErrorCodes
from .services.jwt import Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/login")


async def get_user(token: str = Depends(oauth2_scheme)):
    return Token.get_access_token_user(token)


async def get_superuser(user=Depends(get_user)):
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AccountErrorCodes.AccessDenied
        )
    return user
