from datetime import timedelta
from pathlib import Path

MAX_FILE_SIZE = 5  # int number as MB

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
#  Path.cwd() / "static"
BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
products_list_limit = 12

TOTP_EXPIRATION_SECONDS = 90

SECRET_KEY = '85bb38db2f01f7ab8fe3d7a5180008a8b6d8b8b126ab07c8178c8c5c536984e5'

ACCESS_TOKEN_EXPIRE_TIME = timedelta(minutes=10)
REFRESH_TOKEN_EXPIRE_TIME = timedelta(days=1)
