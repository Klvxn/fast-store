from fastapi import APIRouter, status

from . import schemas
from .services import totp
from .services.email import EmailHandler
from .services.jwt import Token
from .services.manager import UserManager

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


# TODO: Add description, tags, summary, response to routers

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserSchema
)
async def register(user_data: schemas.UserRegisterSchema):
    user = UserManager.create_user(user_data.model_dump(exclude={"confirm"}))
    EmailHandler.send_totp_email(totp.generate_totp(user.totp_secret))
    return schemas.UserSchema.model_validate(user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TokenObtainSchema
)
async def login(login_data: schemas.UserLogInSchema):
    user = UserManager.authenticate(login_data.model_dump())
    user_tokens = Token.for_user(user)
    return schemas.TokenObtainSchema(**user_tokens)


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSchema,
)
async def verify(verification_data: schemas.UserVerifySchema):
    verified_user = UserManager.verify(verification_data.model_dump())
    return schemas.UserSchema.model_validate(verified_user)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TokenRefreshOutSchema
)
async def refresh(refresh_data: schemas.TokenRefreshInSchema):
    payload = Token.decode(refresh_data.refresh)
    user = Token.get_user_from_payload(payload)
    access_token = Token.create_access_token(user.id)
    UserManager.update_last_login(user.id)
    return schemas.TokenRefreshOutSchema(access=access_token)
