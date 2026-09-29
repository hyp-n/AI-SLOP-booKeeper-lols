from flask import Blueprint, request, jsonify
from models import db, User, FriendRequest, Book
from routes.auth import token_required

social_bp = Blueprint("social", __name__)


@social_bp.route("/friends", methods=["GET"])
@token_required
def get_friends(user):
    """Get all accepted friends."""
    sent = FriendRequest.query.filter_by(sender_id=user.id, status="accepted").all()
    received = FriendRequest.query.filter_by(receiver_id=user.id, status="accepted").all()

    friend_ids = set()
    for fr in sent:
        friend_ids.add(fr.receiver_id)
    for fr in received:
        friend_ids.add(fr.sender_id)

    friends = User.query.filter(User.id.in_(friend_ids)).all() if friend_ids else []
    return jsonify([f.to_dict() for f in friends])


@social_bp.errorhandler(404)
def social_not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@social_bp.route("/friends/requests", methods=["GET"])
@token_required
def get_friend_requests(user):
    """Get pending friend requests."""
    received = FriendRequest.query.filter_by(receiver_id=user.id, status="pending").all()
    sent = FriendRequest.query.filter_by(sender_id=user.id, status="pending").all()

    return jsonify({
        "received": [{
            "id": fr.id,
            "sender": fr.sender_id,
            "receiver": fr.receiver_id,
            "status": fr.status,
            "created_at": fr.created_at.isoformat() if fr.created_at else None,
        } for fr in received],
        "sent": [{
            "id": fr.id,
            "sender": fr.sender_id,
            "receiver": fr.receiver_id,
            "status": fr.status,
            "created_at": fr.created_at.isoformat() if fr.created_at else None,
        } for fr in sent],
    })


@social_bp.errorhandler(500)
def social_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


@social_bp.route("/friends/request", methods=["POST"])
@token_required
def send_friend_request(user):
    """Send a friend request."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    friend_email = data.get("email", "").strip().lower()

    if not friend_email:
        return jsonify({"error": "Email required"}), 400

    if "@" not in friend_email:
        return jsonify({"error": "Invalid email format"}), 400

    friend = User.query.filter_by(email=friend_email).first()
    if not friend:
        return jsonify({"error": "User not found"}), 404

    if friend.id == user.id:
        return jsonify({"error": "Cannot friend yourself"}), 400

    # Check if already friends or pending
    existing = FriendRequest.query.filter_by(
        sender_id=user.id, receiver_id=friend.id, status="pending"
    ).first()
    if existing:
        return jsonify({"error": "Request already sent"}), 409

    existing_reverse = FriendRequest.query.filter_by(
        sender_id=friend.id, receiver_id=user.id, status="pending"
    ).first()
    if existing_reverse:
        return jsonify({"error": "They already sent you a request"}), 409

    already_friends = FriendRequest.query.filter_by(
        sender_id=user.id, receiver_id=friend.id, status="accepted"
    ).first()
    if already_friends:
        return jsonify({"error": "Already friends"}), 409

    fr = FriendRequest(
        sender_id=user.id,
        receiver_id=friend.id,
        status="pending",
    )

    db.session.add(fr)
    db.session.commit()

    return jsonify({
        "id": fr.id,
        "sender": fr.sender_id,
        "receiver": fr.receiver_id,
        "status": fr.status,
        "created_at": fr.created_at.isoformat() if fr.created_at else None,
    }), 201


@social_bp.route("/friends/accept/<request_id>", methods=["PUT"])
@token_required
def accept_friend_request(user, request_id):
    """Accept a friend request."""
    fr = FriendRequest.query.get(request_id)
    if not fr:
        return jsonify({"error": "Request not found"}), 404

    if fr.receiver_id != user.id:
        return jsonify({"error": "Not authorized"}), 403

    if fr.status != "pending":
        return jsonify({"error": "Request is not pending"}), 400

    fr.status = "accepted"
    db.session.commit()

    return jsonify({
        "id": fr.id,
        "sender": fr.sender_id,
        "receiver": fr.receiver_id,
        "status": fr.status,
        "created_at": fr.created_at.isoformat() if fr.created_at else None,
    })


@social_bp.route("/friends/decline/<request_id>", methods=["PUT"])
@token_required
def decline_friend_request(user, request_id):
    """Decline a friend request."""
    fr = FriendRequest.query.get(request_id)
    if not fr:
        return jsonify({"error": "Request not found"}), 404

    if fr.receiver_id != user.id:
        return jsonify({"error": "Not authorized"}), 403

    if fr.status != "pending":
        return jsonify({"error": "Request is not pending"}), 400

    fr.status = "declined"
    db.session.commit()

    return jsonify({
        "id": fr.id,
        "sender": fr.sender_id,
        "receiver": fr.receiver_id,
        "status": fr.status,
        "created_at": fr.created_at.isoformat() if fr.created_at else None,
    })


@social_bp.route("/friends/<friend_id>", methods=["DELETE"])
@token_required
def remove_friend(user, friend_id):
    """Remove a friend."""
    FriendRequest.query.filter(
        db.or_(
            db.and_(FriendRequest.sender_id == user.id, FriendRequest.receiver_id == friend_id),
            db.and_(FriendRequest.receiver_id == user.id, FriendRequest.sender_id == friend_id),
        )
    ).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({"message": "Friend removed"})


@social_bp.route("/users/search", methods=["GET"])
@token_required
def search_users(user):
    """Search users by name or email."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    if len(q) > 100:
        return jsonify({"error": "Search query too long"}), 400

    like = f"%{q}%"
    users = User.query.filter(
        db.or_(
            User.email.ilike(like),
            User.name.ilike(like),
        ),
        User.id != user.id
    ).limit(10).all()

    return jsonify([u.to_dict() for u in users])


@social_bp.route("/users/<user_id>", methods=["GET"])
@token_required
def get_user_profile(user, user_id):
    """Get a user's public profile."""
    if not user_id or len(user_id) > 36:
        return jsonify({"error": "Invalid user ID"}), 400
    profile_user = User.query.get(user_id)
    if not profile_user:
        return jsonify({"error": "User not found"}), 404

    result = profile_user.to_dict()

    # Add currently reading book info
    if profile_user.currently_reading:
        book = Book.query.get(profile_user.currently_reading)
        if book:
            result["currently_reading_book"] = book.to_dict()

    # Check friendship status
    fr = FriendRequest.query.filter_by(
        sender_id=user.id, receiver_id=profile_user.id
    ).first() or FriendRequest.query.filter_by(
        sender_id=profile_user.id, receiver_id=user.id
    ).first()

    if fr:
        result["friendship_status"] = fr.status
        result["friend_request_id"] = fr.id
    else:
        result["friendship_status"] = None

    return jsonify(result)


@social_bp.errorhandler(400)
def social_bad_request(e):
    return jsonify({"error": "Bad request"}), 400