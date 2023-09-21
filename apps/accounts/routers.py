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


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserSchema
)
def register(user_data: schemas.UserRegisterSchema):
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
def login(login_data: schemas.UserLogInSchema):
    user = authenticate(**login_data.model_dump())

    user_tokens = Token.for_user(user)

    return schemas.TokenObtainSchema(**user_tokens)
