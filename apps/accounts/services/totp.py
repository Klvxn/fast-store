from pyotp import TOTP, random_base32

# todo: WHAT IF NOT ADDED?
from config.settings import TOTP_EXPIRATION_TIME


def generate_secret():
    return random_base32()


def generate_totp(secret: str):
    totp = TOTP(secret, interval=TOTP_EXPIRATION_TIME)
    return totp.now()


def verify_totp(secret: str, user_totp: str):
    totp = TOTP(secret, interval=TOTP_EXPIRATION_TIME)
    return totp.verify(user_totp)
