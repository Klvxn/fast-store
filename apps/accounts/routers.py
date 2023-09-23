from fastapi import APIRouter, HTTPException, status

from . import schemas
from .models import User
from .services import totp
from .services.authentication import authenticate
from .services.email import EmailHandler
from .services.hash import Hash
from .services.jwt import Token

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
    if User.filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered"
        )

    user_dict = user_data.model_dump(exclude={"confirm"})
    user_dict["password"] = Hash.hash_password(user_dict["password"])
    user_dict["totp_secret"] = totp.generate_secret()

    user = User.create(**user_dict)

    EmailHandler.send_totp_email(totp.generate_totp(user_dict["totp_secret"]))
    return schemas.UserSchema.model_validate(user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TokenObtainSchema
)
async def login(login_data: schemas.UserLogInSchema):
    user = authenticate(**login_data.model_dump())

    user_tokens = Token.for_user(user)

    return schemas.TokenObtainSchema(**user_tokens)


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSchema,
)
async def verify(verification_data: schemas.UserVerifySchema):
    user = User.filter(User.email == verification_data.email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is already verified"
        )

    if not totp.verify_totp(user.totp_secret, verification_data.totp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is invalid or expired"
        )
    User.update(user.id, is_verified=True, totp_secret=None)
    return schemas.UserSchema.model_validate(user)
