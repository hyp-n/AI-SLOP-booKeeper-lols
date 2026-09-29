"""Socket.IO handlers for real-time messaging.

Each connection authenticates with the same JWT used by the REST API. Messages
posted over the socket are persisted to PostgreSQL by the same code path used
by `POST /api/messages/conversations/<id>/messages`, so REST and socket clients
stay in sync.
"""
import jwt
from flask import current_app
from flask_socketio import emit, join_room, leave_room

from models import db, Conversation, ConversationParticipant, Message, User


def _authenticate(auth_token):
    """Resolve a JWT to a user, or None if invalid/expired."""
    if not auth_token:
        return None
    try:
        payload = jwt.decode(
            auth_token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
    except Exception:
        return None
    return User.query.get(payload.get("user_id"))


def _is_member(conversation_id, user_id):
    if not conversation_id or not user_id:
        return False
    return ConversationParticipant.query.filter_by(
        conversation_id=conversation_id, user_id=user_id
    ).first() is not None


def register_socket_handlers(socketio):
    @socketio.on("connect")
    def handle_connect(auth=None):
        token = (auth or {}).get("token") if isinstance(auth, dict) else None
        if not token and isinstance(auth, str):
            token = auth
        user = _authenticate(token)
        if not user:
            return False
        from flask import request as flask_request

        flask_request.environ["user"] = user
        emit("connected", {"user_id": user.id})
        return True

    @socketio.on("join_conversation")
    def handle_join(data):
        from flask import request as flask_request

        user = flask_request.environ.get("user")
        if not user:
            emit("error", {"error": "unauthorized"})
            return

        conv_id = (data or {}).get("conversation_id")
        if not _is_member(conv_id, user.id):
            emit("error", {"error": "not a participant"})
            return

        join_room(str(conv_id))
        emit("joined", {"conversation_id": str(conv_id)})

    @socketio.on("leave_conversation")
    def handle_leave(data):
        conv_id = (data or {}).get("conversation_id")
        if conv_id:
            leave_room(str(conv_id))

    @socketio.on("send_message")
    def handle_send(data):
        from flask import request as flask_request

        user = flask_request.environ.get("user")
        if not user:
            emit("error", {"error": "unauthorized"})
            return

        data = data or {}
        conv_id = data.get("conversation_id")
        content = (data.get("content") or "").strip()
        if not content:
            emit("error", {"error": "content required"})
            return
        if len(content) > 4000:
            emit("error", {"error": "message too long"})
            return

        if not _is_member(conv_id, user.id):
            emit("error", {"error": "not a participant"})
            return

        msg = Message(
            sender_id=user.id,
            conversation_id=conv_id,
            content=content,
            read_by=[user.id],
        )
        db.session.add(msg)

        conv = Conversation.query.get(conv_id)
        if conv:
            conv.last_message_at = msg.created_at

        db.session.commit()

        payload = msg.to_dict()
        emit("new_message", payload, to=str(conv_id))

    @socketio.on("typing")
    def handle_typing(data):
        from flask import request as flask_request

        user = flask_request.environ.get("user")
        if not user:
            return
        conv_id = (data or {}).get("conversation_id")
        if not _is_member(conv_id, user.id):
            return
        emit(
            "user_typing",
            {
                "conversation_id": str(conv_id),
                "user_id": user.id,
                "name": user.name or user.email,
                "is_typing": bool((data or {}).get("is_typing", True)),
            },
            to=str(conv_id),
            include_self=False,
        )