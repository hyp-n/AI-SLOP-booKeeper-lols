from flask import Blueprint, request, jsonify, current_app
from models import get_users_collection, user_to_dict, to_object_id, utcnow
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps

auth_bp = Blueprint("auth", __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user = get_users_collection(current_app.mongo).find_one({"_id": to_object_id(data["user_id"])})
            if not user:
                return jsonify({"error": "User not found"}), 401
        except:
            return jsonify({"error": "Invalid token"}), 401
        return f(user, *args, **kwargs)
    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    mongo = current_app.mongo
    users_coll = get_users_collection(mongo)

    if users_coll.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = {
        "email": email,
        "password_hash": password_hash,
        "name": name,
        "avatar_url": None,
        "bio": "",
        "currently_reading": None,
        "oauth_provider": None,
        "oauth_id": None,
        "created_at": utcnow(),
        "last_login": None,
    }

    result = users_coll.insert_one(user)
    user["_id"] = result.inserted_id

    token = jwt.encode(
        {"user_id": str(user["_id"]), "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token, "user": user_to_dict(user)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    mongo = current_app.mongo
    users_coll = get_users_collection(mongo)

    user = users_coll.find_one({"email": email})
    if not user or not user.get("password_hash"):
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    users_coll.update_one({"_id": user["_id"]}, {"$set": {"last_login": utcnow()}})

    token = jwt.encode(
        {"user_id": str(user["_id"]), "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token, "user": user_to_dict(user)})


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me(user):
    return jsonify(user_to_dict(user))


@auth_bp.route("/me", methods=["PUT"])
@token_required
def update_me(user):
    data = request.get_json()
    mongo = current_app.mongo
    users_coll = get_users_collection(mongo)

    update_fields = {}
    if "name" in data:
        update_fields["name"] = data["name"]
    if "bio" in data:
        update_fields["bio"] = data["bio"]
    if "avatar_url" in data:
        update_fields["avatar_url"] = data["avatar_url"]
    if "currently_reading" in data:
        update_fields["currently_reading"] = to_object_id(data["currently_reading"])

    if update_fields:
        users_coll.update_one({"_id": user["_id"]}, {"$set": update_fields})
        user.update(update_fields)

    return jsonify(user_to_dict(user))
