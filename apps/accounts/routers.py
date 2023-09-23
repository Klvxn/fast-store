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
    user = await UserManager.create(user_data.model_dump(exclude={"confirm"}))
    EmailHandler.send_totp_email(totp.generate_totp(user.totp_secret))
    return schemas.UserSchema.model_validate(user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TokenObtainSchema
)
async def login(login_data: schemas.UserLogInSchema):
    user = await UserManager.authenticate(login_data.model_dump())
    user_tokens = Token.for_user(user)
    return schemas.TokenObtainSchema(**user_tokens)


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSchema,
)
async def verify(verification_data: schemas.UserVerifySchema):
    verified_user = await UserManager.verify(verification_data.model_dump())
    return schemas.UserSchema.model_validate(verified_user)

    if not totp.verify_totp(user.totp_secret, verification_data.totp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is invalid or expired"
        )
    User.update(user.id, is_verified=True, totp_secret=None)
    return schemas.UserSchema.model_validate(user)
