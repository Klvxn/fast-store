from fastapi import HTTPException, status

EmailInUse = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="This email is already registered"
)

InvalidCredentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Wrong Email or password"
)

UserNotVerified = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User account is not verified"
)

InactiveAccount = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User account is banned"
)

AlreadyVerified = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="This user is already verified"
)

InvalidTOTP = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="TOTP is invalid or expired"
)

InvalidVerification = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid verification"
)
