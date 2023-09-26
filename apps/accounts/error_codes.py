class AccountErrorCodes:
    EmailInUse = "This email is already registered"
    InvalidCredentials = "Wrong Email or password"
    UserNotVerified = "User account is not verified"
    InactiveAccount = "User account is banned"
    AlreadyVerified = "This user is already verified"
    InvalidTOTP = "TOTP is invalid or expired"
    InvalidVerification = "Invalid verification"
    InvalidJWT = "Invalid JWT"
