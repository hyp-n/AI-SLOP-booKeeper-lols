from flask import Blueprint, request, jsonify
from models import db, User, Conversation, ConversationParticipant, Message
from routes.auth import token_required

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/conversations", methods=["GET"])
@token_required
def get_conversations(user):
    """Get all conversations for the current user."""
    # Get conversations where user is a participant
    convs = (
        Conversation.query.join(
            ConversationParticipant, Conversation.id == ConversationParticipant.conversation_id
        )
        .filter(ConversationParticipant.user_id == user.id)
        .order_by(Conversation.last_message_at.desc().nullslast())
        .all()
    )

    if not convs:
        return jsonify([])

    result = []
    for conv in convs:
        conv_dict = conv.to_dict()
        # Add participant details
        participants = (
            User.query.join(
                ConversationParticipant, User.id == ConversationParticipant.user_id
            )
            .filter(ConversationParticipant.conversation_id == conv.id)
            .all()
        )
        conv_dict["participant_details"] = [p.to_dict() for p in participants]
        # Get last message
        last_msg = (
            Message.query.filter_by(conversation_id=conv.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        if last_msg:
            conv_dict["last_message"] = last_msg.to_dict()
        result.append(conv_dict)

    return jsonify(result)


@messages_bp.route("/conversations", methods=["POST"])
@token_required
def create_conversation(user):
    """Create a 1-on-1 conversation or group chat."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    participant_ids = data.get("participant_ids", [])
    is_group = data.get("is_group", False)
    group_name = data.get("group_name")

    if not participant_ids:
        return jsonify({"error": "participant_ids required"}), 400

    if is_group and not group_name:
        return jsonify({"error": "group_name is required for group chats"}), 400

    if not is_group and len(participant_ids) != 1:
        return jsonify({"error": "1-on-1 conversations require exactly 1 participant"}), 400

    # Check if 1-on-1 conversation already exists
    if not is_group and len(participant_ids) == 1:
        other_user_id = participant_ids[0]
        existing = (
            Conversation.query.join(
                ConversationParticipant, Conversation.id == ConversationParticipant.conversation_id
            )
            .filter(
                Conversation.is_group == False,
                ConversationParticipant.user_id.in_([user.id, other_user_id]),
            )
            .group_by(Conversation.id)
            .having(db.func.count(ConversationParticipant.id) == 2)
            .first()
        )
        if existing:
            return jsonify(existing.to_dict()), 200

    # Create conversation
    conv = Conversation(
        is_group=is_group,
        group_name=group_name if is_group else None,
        group_admin=user.id if is_group else None,
    )

    db.session.add(conv)
    db.session.flush()  # Get the ID

    # Add participants
    cp = ConversationParticipant(conversation_id=conv.id, user_id=user.id)
    db.session.add(cp)
    for pid in participant_ids:
        if pid == user.id:
            continue
        cp = ConversationParticipant(conversation_id=conv.id, user_id=pid)
        db.session.add(cp)

    db.session.commit()
    return jsonify(conv.to_dict()), 201


@messages_bp.route("/conversations/<conv_id>/messages", methods=["GET"])
@token_required
def get_messages(user, conv_id):
    """Get messages in a conversation."""
    if not conv_id or len(conv_id) > 36:
        return jsonify({"error": "Invalid conversation ID"}), 400
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    # Check if user is a participant
    is_participant = ConversationParticipant.query.filter_by(
        conversation_id=conv_id, user_id=user.id
    ).first()
    if not is_participant:
        return jsonify({"error": "Not authorized"}), 403

    messages = (
        Message.query.filter_by(conversation_id=conv_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    return jsonify([m.to_dict() for m in messages])


@messages_bp.route("/conversations/<conv_id>/messages", methods=["POST"])
@token_required
def send_message(user, conv_id):
    """Send a message in a conversation."""
    if not conv_id or len(conv_id) > 36:
        return jsonify({"error": "Invalid conversation ID"}), 400
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    # Check if user is a participant
    is_participant = ConversationParticipant.query.filter_by(
        conversation_id=conv_id, user_id=user.id
    ).first()
    if not is_participant:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Content required"}), 400

    if len(content) > 4000:
        return jsonify({"error": "Message too long (max 4000 characters)"}), 400

    msg = Message(
        sender_id=user.id,
        conversation_id=conv_id,
        content=content,
        read_by=[user.id],
    )

    db.session.add(msg)
    conv.last_message_at = msg.created_at
    db.session.commit()

    return jsonify(msg.to_dict()), 201


@messages_bp.route("/conversations/<conv_id>/group/add", methods=["POST"])
@token_required
def add_to_group(user, conv_id):
    """Add a member to a group chat."""
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    if not conv.is_group:
        return jsonify({"error": "Not a group chat"}), 400

    if conv.group_admin != user.id:
        return jsonify({"error": "Only group admin can add members"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    new_member_id = data.get("user_id")

    if not new_member_id:
        return jsonify({"error": "user_id required"}), 400

    if new_member_id == user.id:
        return jsonify({"error": "You are already a member"}), 400

    # Check if already a member
    existing = ConversationParticipant.query.filter_by(
        conversation_id=conv_id, user_id=new_member_id
    ).first()
    if not existing:
        cp = ConversationParticipant(conversation_id=conv_id, user_id=new_member_id)
        db.session.add(cp)
        db.session.commit()

    conv = Conversation.query.get(conv_id)
    return jsonify(conv.to_dict())


@messages_bp.route("/conversations/<conv_id>/group/rename", methods=["PUT"])
@token_required
def rename_group(user, conv_id):
    """Rename a group chat."""
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    if not conv.is_group:
        return jsonify({"error": "Not a group chat"}), 400

    if conv.group_admin != user.id:
        return jsonify({"error": "Only group admin can rename"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    new_name = data.get("name", "").strip()

    if not new_name:
        return jsonify({"error": "Name required"}), 400

    if len(new_name) > 200:
        return jsonify({"error": "Name must be 200 characters or less"}), 400

    conv.group_name = new_name
    db.session.commit()

    return jsonify(conv.to_dict())


@messages_bp.errorhandler(404)
def message_not_found(e):
    return jsonify({"error": "Conversation not found"}), 404


@messages_bp.errorhandler(500)
def message_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500