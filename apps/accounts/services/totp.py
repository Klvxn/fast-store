from pyotp import TOTP, random_base32

from apps.core.exceptions import ImproperlyConfigured

try:
    from config.settings import TOTP_EXPIRATION_SECONDS
except ImportError:
    raise ImproperlyConfigured("TOTP_EXPIRATION_SECONDS is not added to settings")


def generate_secret():
    return random_base32()


def generate_totp(secret: str):
    totp = TOTP(secret, interval=TOTP_EXPIRATION_SECONDS)
    return totp.now()


def verify_totp(secret: str, user_totp: str):
    totp = TOTP(secret, interval=TOTP_EXPIRATION_SECONDS)
    return totp.verify(user_totp)
