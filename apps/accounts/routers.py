from fastapi import APIRouter, status

from . import schemas
from .services import totp
from .services.email import EmailHandler
from .services.jwt import Token
from .services.manager import UserManager

router = APIRouter(
    prefix="/accounts",
    tags=["Authentication"]
)


# TODO: Add description, tags, summary, response to routers

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserSchema,
    summary='Register a new user',
    description='Register a new user by email,for now with email.')
# TODO rename `user_data` to `register`
async def register(user_data: schemas.UserRegisterSchema):
    # TODO create a new class `OAuthService` and move the code block to it.
    # example: registered = OAuthService.register(**register.model_dump())
    user = UserManager.create_user(user_data.model_dump(exclude={"confirm"}))

    # TODO move this code to `OAuthService.register`
    EmailHandler.send_totp_email(totp.generate_totp(user.totp_secret))

    # TODO `return {'register': register}` , or ask from AI
    return schemas.UserSchema.model_validate(user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TokenObtainSchema,
    summary='Login with provided credentials',
    description='Login with provided credentials, for now with email and password.')
# TODO rename `login_data` to `login`
async def login(login_data: schemas.UserLogInSchema):
    # TODO add new method `.authenticate()` to `OAuthService`
    # example: logged = OAuthService.authenticate(**login.model_dump())
    user = UserManager.authenticate(login_data.model_dump())

    # TODO move this code to `OAuthService.authenticate`
    user_tokens = Token.for_user(user)

    # TODO return {'Token': user_tokens}, or ask from AI
    return schemas.TokenObtainSchema(**user_tokens)


# TODO remove this section `verify` and do verification in the `register` endpoint
@router.post(
    "/verify",
    # TODO change endpoint url to "/register/confirm",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSchema,

    summary='',
    description='')
async def verify(verification_data: schemas.UserVerifySchema):
    verified_user = UserManager.verify(verification_data.model_dump())
    return schemas.UserSchema.model_validate(verified_user)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TokenRefreshOutSchema,
    summary='',
    description='')
# TODO rename `refresh_data` to `refresh`
async def refresh(refresh_data: schemas.TokenRefreshInSchema):
    # TODO add new method `.refresh_token(refresh)` to `OAuthService`
    # example: new_token = OAuthService.refresh_token(**refresh.model_dump())

    # TODO move this code to `OAuthService.refresh_token`
    user = Token.get_refresh_token_user(refresh_data.refresh)
    access_token = Token.create_access_token(user)
    UserManager.update_last_login(user.id)

    # TODO return {'Token': new_token}, or ask from AI
    return schemas.TokenRefreshOutSchema(access=access_token)

# --- when internet connected ---
# TODO 1. search about the endpoints names (for JWT and user authentications) and use AI
# TODO --- commit changes ---

# TODO 2. search for endpoint descriptions ans summary and use AI
# TODO --- commit changes ---

# TODO 3. (refactor) rename the schemas class
# TODO --- commit changes ---

# TODO 4. (refactor) move the BL to service file
# TODO --- commit for every method refactor ---
