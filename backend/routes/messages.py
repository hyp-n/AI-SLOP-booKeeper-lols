from flask import Blueprint, request, jsonify, current_app
from models import (
    get_users_collection, get_messages_collection, get_conversations_collection,
    message_to_dict, conversation_to_dict, to_object_id, utcnow
)
from routes.auth import token_required
from datetime import datetime, timezone

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/conversations", methods=["GET"])
@token_required
def get_conversations(user):
    """Get all conversations for the current user."""
    mongo = current_app.mongo
    conv_coll = get_conversations_collection(mongo)
    users_coll = get_users_collection(mongo)
    msg_coll = get_messages_collection(mongo)

    conversations = list(conv_coll.find({"participants": user["_id"]}).sort("last_message_at", -1))

    result = []
    for conv in conversations:
        conv_dict = conversation_to_dict(conv)
        # Add participant details
        participants = list(users_coll.find({"_id": {"$in": conv["participants"]}}))
        conv_dict["participant_details"] = [user_to_dict(p) for p in participants]
        # Get last message
        last_msg = msg_coll.find_one({"conversation_id": conv["_id"]}, sort=[("created_at", -1)])
        if last_msg:
            conv_dict["last_message"] = message_to_dict(last_msg)
        result.append(conv_dict)

    return jsonify(result)


@messages_bp.route("/conversations", methods=["POST"])
@token_required
def create_conversation(user):
    """Create a 1-on-1 conversation or group chat."""
    data = request.get_json()
    participant_ids = data.get("participant_ids", [])
    is_group = data.get("is_group", False)
    group_name = data.get("group_name")

    if not participant_ids:
        return jsonify({"error": "participant_ids required"}), 400

    mongo = current_app.mongo
    conv_coll = get_conversations_collection(mongo)

    # Check if 1-on-1 conversation already exists
    if not is_group and len(participant_ids) == 1:
        other_user_id = to_object_id(participant_ids[0])
        existing = conv_coll.find_one({
            "participants": {"$all": [user["_id"], other_user_id]},
            "is_group": False,
        })
        if existing:
            return jsonify(conversation_to_dict(existing)), 200

    # Create conversation
    participants = [user["_id"]] + [to_object_id(pid) for pid in participant_ids]
    conv = {
        "participants": participants,
        "is_group": is_group,
        "group_name": group_name if is_group else None,
        "group_admin": user["_id"] if is_group else None,
        "created_at": utcnow(),
        "last_message_at": None,
    }

    result = conv_coll.insert_one(conv)
    conv["_id"] = result.inserted_id

    return jsonify(conversation_to_dict(conv)), 201


@messages_bp.route("/conversations/<conv_id>/messages", methods=["GET"])
@token_required
def get_messages(user, conv_id):
    """Get messages in a conversation."""
    mongo = current_app.mongo
    conv_coll = get_conversations_collection(mongo)
    msg_coll = get_messages_collection(mongo)

    conv = conv_coll.find_one({"_id": to_object_id(conv_id)})
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    if user["_id"] not in conv["participants"]:
        return jsonify({"error": "Not authorized"}), 403

    messages = list(msg_coll.find({"conversation_id": conv["_id"]}).sort("created_at", 1))
    return jsonify([message_to_dict(m) for m in messages])


@messages_bp.route("/conversations/<conv_id>/messages", methods=["POST"])
@token_required
def send_message(user, conv_id):
    """Send a message in a conversation."""
    mongo = current_app.mongo
    conv_coll = get_conversations_collection(mongo)
    msg_coll = get_messages_collection(mongo)

    conv = conv_coll.find_one({"_id": to_object_id(conv_id)})
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    if user["_id"] not in conv["participants"]:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Content required"}), 400

    msg = {
        "sender": user["_id"],
        "conversation_id": conv["_id"],
        "content": content,
        "created_at": utcnow(),
        "read_by": [],
    }

    result = msg_coll.insert_one(msg)
    msg["_id"] = result.inserted_id

    # Update conversation last_message_at
    conv_coll.update_one({"_id": conv["_id"]}, {"$set": {"last_message_at": utcnow()}})

    return jsonify(message_to_dict(msg)), 201


@messages_bp.route("/conversations/<conv_id>/group/add", methods=["POST"])
@token_required
def add_to_group(user, conv_id):
    """Add a member to a group chat."""
    mongo = current_app.mongo
    conv_coll = get_conversations_collection(mongo)

    conv = conv_coll.find_one({"_id": to_object_id(conv_id)})
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    if not conv.get("is_group"):
        return jsonify({"error": "Not a group chat"}), 400

    if conv.get("group_admin") != user["_id"]:
        return jsonify({"error": "Only group admin can add members"}), 403

    data = request.get_json()
    new_member_id = to_object_id(data.get("user_id"))

    if not new_member_id:
        return jsonify({"error": "user_id required"}), 400

    if new_member_id not in conv["participants"]:
        conv_coll.update_one({"_id": conv["_id"]}, {"$push": {"participants": new_member_id}})

    conv = conv_coll.find_one({"_id": conv["_id"]})
    return jsonify(conversation_to_dict(conv))


@messages_bp.route("/conversations/<conv_id>/group/rename", methods=["PUT"])
@token_required
def rename_group(user, conv_id):
    """Rename a group chat."""
    mongo = current_app.mongo
    conv_coll = get_conversations_collection(mongo)

    conv = conv_coll.find_one({"_id": to_object_id(conv_id)})
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    if not conv.get("is_group"):
        return jsonify({"error": "Not a group chat"}), 400

    if conv.get("group_admin") != user["_id"]:
        return jsonify({"error": "Only group admin can rename"}), 403

    data = request.get_json()
    new_name = data.get("name", "").strip()

    if not new_name:
        return jsonify({"error": "Name required"}), 400

    conv_coll.update_one({"_id": conv["_id"]}, {"$set": {"group_name": new_name}})
    conv["group_name"] = new_name

    return jsonify(conversation_to_dict(conv))
