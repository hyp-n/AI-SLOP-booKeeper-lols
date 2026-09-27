import os
import secrets
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# MongoDB configuration
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/bookeeper")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "bookeeper")

# An Atlas `mongodb+srv://` URI often has no database in its path. Flask-PyMongo
# resolves the database from the URI, so fall back to the explicit name rather
# than leaving `mongo.db` as None (which fails only on the first query).
if "/" not in MONGODB_URI.split("://", 1)[-1].split("?", 1)[0].split("@")[-1]:
    MONGODB_URI = f"{MONGODB_URI.rstrip('/')}/{MONGODB_DB_NAME}"

# SECRET_KEY must stay stable across restarts or every issued JWT is invalidated
# on the next boot. Generate once and cache it on disk, never per-process.
_SECRET_FILE = os.path.join(DATA_DIR, ".secret_key")


def _get_secret_key():
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    if os.path.exists(_SECRET_FILE):
        with open(_SECRET_FILE, "r", encoding="utf-8") as f:
            cached = f.read().strip()
        if cached:
            return cached
    generated = secrets.token_hex(32)
    with open(_SECRET_FILE, "w", encoding="utf-8") as f:
        f.write(generated)
    return generated


SECRET_KEY = _get_secret_key()
SECRET_FILE_PATH = _SECRET_FILE

# Token lifetime
JWT_EXPIRY_DAYS = int(os.environ.get("JWT_EXPIRY_DAYS", "30"))

# Google OAuth (leave blank to disable the Google login button)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

# Comma-separated list of allowed browser origins
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS", "http://localhost:5000,http://localhost:5173"
    ).split(",")
    if o.strip()
]

FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
