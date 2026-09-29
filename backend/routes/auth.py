from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from models import db, User
import bcrypt
import jwt
import requests
from datetime import datetime, timezone, timedelta
from functools import wraps
from urllib.parse import urlencode

auth_bp = Blueprint("auth", __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user = User.query.get(data["user_id"])
            if not user:
                return jsonify({"error": "User not found"}), 401
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(user, *args, **kwargs)
    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = User(
        email=email,
        password_hash=password_hash,
        name=name,
        avatar_url=None,
        bio="",
        currently_reading=None,
        oauth_provider=None,
        oauth_id=None,
    )

    db.session.add(user)
    db.session.commit()

    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + timedelta(days=current_app.config.get("JWT_EXPIRY_DAYS", 7))},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + timedelta(days=current_app.config.get("JWT_EXPIRY_DAYS", 7))},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token, "user": user.to_dict()})


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me(user):
    return jsonify(user.to_dict())


@auth_bp.route("/me", methods=["PUT"])
@token_required
def update_me(user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    if "name" in data:
        user.name = data["name"]
    if "bio" in data:
        user.bio = data["bio"]
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
    if "currently_reading" in data:
        user.currently_reading = data["currently_reading"]

    db.session.commit()
    return jsonify(user.to_dict())


@auth_bp.errorhandler(400)
def auth_bad_request(e):
    return jsonify({"error": "Bad request"}), 400


@auth_bp.errorhandler(404)
def auth_not_found(e):
    return jsonify({"error": "User not found"}), 404


@auth_bp.route("/google/login")
def google_login():
    """Redirect to Google OAuth consent screen."""
    client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")
    if not client_id:
        return jsonify({"error": "Google OAuth not configured"}), 500

    redirect_uri = url_for("auth.google_callback", _external=True)
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
    }
    google_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return redirect(google_url)


@auth_bp.route("/google/callback")
def google_callback():
    """Handle Google OAuth callback."""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code missing"}), 400

    client_id = current_app.config.get("GOOGLE_CLIENT_ID", "")
    client_secret = current_app.config.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = url_for("auth.google_callback", _external=True)

    # Exchange code for tokens
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    if token_resp.status_code != 200:
        return jsonify({"error": "Failed to obtain access token"}), 401

    tokens = token_resp.json()
    access_token = tokens.get("access_token")

    # Get user info from Google
    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if userinfo_resp.status_code != 200:
        return jsonify({"error": "Failed to get user info"}), 401

    google_user = userinfo_resp.json()
    email = google_user.get("email", "").lower()
    name = google_user.get("name", "")
    picture = google_user.get("picture", "")
    google_id = google_user.get("sub", "")

    # Find or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            password_hash=None,
            name=name,
            avatar_url=picture,
            bio="",
            currently_reading=None,
            oauth_provider="google",
            oauth_id=google_id,
        )
        db.session.add(user)
        db.session.commit()
    elif user.oauth_provider != "google":
        # Link existing account to Google
        user.oauth_provider = "google"
        user.oauth_id = google_id
        db.session.commit()

    # Issue JWT
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + timedelta(days=current_app.config.get("JWT_EXPIRY_DAYS", 7))},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    # Redirect to frontend with token
    frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5000")
    return redirect(f"{frontend_url}/login?token={token}")


@auth_bp.errorhandler(500)
def auth_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500