from flask import Blueprint, request, jsonify, current_app
from models import (
    get_users_collection, get_friend_requests_collection,
    get_books_collection, user_to_dict, book_to_dict, to_object_id, utcnow
)
from routes.auth import token_required
from bson.objectid import ObjectId

social_bp = Blueprint("social", __name__)


@social_bp.route("/friends", methods=["GET"])
@token_required
def get_friends(user):
    """Get all accepted friends."""
    mongo = current_app.mongo
    fr_coll = get_friend_requests_collection(mongo)

    sent = fr_coll.find({"sender": user["_id"], "status": "accepted"})
    received = fr_coll.find({"receiver": user["_id"], "status": "accepted"})

    friend_ids = set()
    for fr in sent:
        friend_ids.add(fr["receiver"])
    for fr in received:
        friend_ids.add(fr["sender"])

    users_coll = get_users_collection(mongo)
    friends = list(users_coll.find({"_id": {"$in": list(friend_ids)}}))
    return jsonify([user_to_dict(f) for f in friends])


@social_bp.route("/friends/requests", methods=["GET"])
@token_required
def get_friend_requests(user):
    """Get pending friend requests."""
    mongo = current_app.mongo
    fr_coll = get_friend_requests_collection(mongo)

    received = list(fr_coll.find({"receiver": user["_id"], "status": "pending"}))
    sent = list(fr_coll.find({"sender": user["_id"], "status": "pending"}))

    return jsonify({
        "received": [{
            "id": str(fr["_id"]),
            "sender": str(fr["sender"]),
            "receiver": str(fr["receiver"]),
            "status": fr["status"],
            "created_at": fr["created_at"].isoformat() if fr.get("created_at") else None,
        } for fr in received],
        "sent": [{
            "id": str(fr["_id"]),
            "sender": str(fr["sender"]),
            "receiver": str(fr["receiver"]),
            "status": fr["status"],
            "created_at": fr["created_at"].isoformat() if fr.get("created_at") else None,
        } for fr in sent],
    })


@social_bp.route("/friends/request", methods=["POST"])
@token_required
def send_friend_request(user):
    """Send a friend request."""
    data = request.get_json()
    friend_email = data.get("email", "").strip().lower()

    if not friend_email:
        return jsonify({"error": "Email required"}), 400

    mongo = current_app.mongo
    users_coll = get_users_collection(mongo)
    fr_coll = get_friend_requests_collection(mongo)

    friend = users_coll.find_one({"email": friend_email})
    if not friend:
        return jsonify({"error": "User not found"}), 404

    if friend["_id"] == user["_id"]:
        return jsonify({"error": "Cannot friend yourself"}), 400

    # Check if already friends or pending
    existing = fr_coll.find_one({"sender": user["_id"], "receiver": friend["_id"], "status": "pending"})
    if existing:
        return jsonify({"error": "Request already sent"}), 409

    existing_reverse = fr_coll.find_one({"sender": friend["_id"], "receiver": user["_id"], "status": "pending"})
    if existing_reverse:
        return jsonify({"error": "They already sent you a request"}), 409

    already_friends = fr_coll.find_one({"sender": user["_id"], "receiver": friend["_id"], "status": "accepted"})
    if already_friends:
        return jsonify({"error": "Already friends"}), 409

    fr = {
        "sender": user["_id"],
        "receiver": friend["_id"],
        "status": "pending",
        "created_at": utcnow(),
    }

    result = fr_coll.insert_one(fr)
    fr["_id"] = result.inserted_id

    return jsonify({
        "id": str(fr["_id"]),
        "sender": str(fr["sender"]),
        "receiver": str(fr["receiver"]),
        "status": fr["status"],
        "created_at": fr["created_at"].isoformat() if fr.get("created_at") else None,
    }), 201


@social_bp.route("/friends/accept/<request_id>", methods=["PUT"])
@token_required
def accept_friend_request(user, request_id):
    """Accept a friend request."""
    mongo = current_app.mongo
    fr_coll = get_friend_requests_collection(mongo)

    fr = fr_coll.find_one({"_id": to_object_id(request_id)})
    if not fr:
        return jsonify({"error": "Request not found"}), 404

    if fr["receiver"] != user["_id"]:
        return jsonify({"error": "Not authorized"}), 403

    fr_coll.update_one({"_id": fr["_id"]}, {"$set": {"status": "accepted"}})
    fr["status"] = "accepted"

    return jsonify({
        "id": str(fr["_id"]),
        "sender": str(fr["sender"]),
        "receiver": str(fr["receiver"]),
        "status": fr["status"],
        "created_at": fr["created_at"].isoformat() if fr.get("created_at") else None,
    })


@social_bp.route("/friends/decline/<request_id>", methods=["PUT"])
@token_required
def decline_friend_request(user, request_id):
    """Decline a friend request."""
    mongo = current_app.mongo
    fr_coll = get_friend_requests_collection(mongo)

    fr = fr_coll.find_one({"_id": to_object_id(request_id)})
    if not fr:
        return jsonify({"error": "Request not found"}), 404

    if fr["receiver"] != user["_id"]:
        return jsonify({"error": "Not authorized"}), 403

    fr_coll.update_one({"_id": fr["_id"]}, {"$set": {"status": "declined"}})
    fr["status"] = "declined"

    return jsonify({
        "id": str(fr["_id"]),
        "sender": str(fr["sender"]),
        "receiver": str(fr["receiver"]),
        "status": fr["status"],
        "created_at": fr["created_at"].isoformat() if fr.get("created_at") else None,
    })


@social_bp.route("/friends/<friend_id>", methods=["DELETE"])
@token_required
def remove_friend(user, friend_id):
    """Remove a friend."""
    mongo = current_app.mongo
    fr_coll = get_friend_requests_collection(mongo)

    fr_coll.delete_many({
        "$or": [
            {"sender": user["_id"], "receiver": to_object_id(friend_id)},
            {"receiver": user["_id"], "sender": to_object_id(friend_id)},
        ]
    })
    return jsonify({"message": "Friend removed"})


@social_bp.route("/users/search", methods=["GET"])
@token_required
def search_users(user):
    """Search users by name or email."""
    q = request.args.get("q", "")
    if not q:
        return jsonify([])

    mongo = current_app.mongo
    users_coll = get_users_collection(mongo)

    users = list(users_coll.find({
        "$or": [
            {"email": {"$regex": q, "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}},
        ],
        "_id": {"$ne": user["_id"]}
    }).limit(10))

    return jsonify([user_to_dict(u) for u in users])


@social_bp.route("/users/<user_id>", methods=["GET"])
@token_required
def get_user_profile(user, user_id):
    """Get a user's public profile."""
    mongo = current_app.mongo
    users_coll = get_users_collection(mongo)

    profile_user = users_coll.find_one({"_id": to_object_id(user_id)})
    if not profile_user:
        return jsonify({"error": "User not found"}), 404

    result = user_to_dict(profile_user)

    # Add currently reading book info
    if profile_user.get("currently_reading"):
        book = get_books_collection(mongo).find_one({"_id": profile_user["currently_reading"]})
        if book:
            result["currently_reading_book"] = book_to_dict(book)

    # Check friendship status
    fr_coll = get_friend_requests_collection(mongo)
    fr = fr_coll.find_one({"sender": user["_id"], "receiver": profile_user["_id"]}) or \
         fr_coll.find_one({"sender": profile_user["_id"], "receiver": user["_id"]})

    if fr:
        result["friendship_status"] = fr["status"]
        result["friend_request_id"] = str(fr["_id"])
    else:
        result["friendship_status"] = None

    return jsonify(result)
