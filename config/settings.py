from datetime import timedelta

# DATABASES = {
#     "drivername": "postgresql",
#     "username": "postgres",
#     "password": "admin",
#     "host": "localhost",
#     "database": "fast_store",
#     "port": 5432
# }
DATABASES = {
    "drivername": "sqlite",
    "database": "fast_store.db"
}

TOTP_EXPIRATION_TIME = timedelta(seconds=90)

SECRET_KEY = '85bb38db2f01f7ab8fe3d7a5180008a8b6d8b8b126ab07c8178c8c5c536984e5'

ACCESS_TOKEN_EXPIRE_TIME = timedelta(minutes=10)
REFRESH_TOKEN_EXPIRE_TIME = timedelta(days=1)
