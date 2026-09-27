"""Socket.IO handlers for real-time messaging.

Each connection authenticates with the same JWT used by the REST API. Messages
posted over the socket are persisted to MongoDB by the same code path used by
`POST /api/messages/conversations/<id>/messages`, so REST and socket clients stay
in sync.
"""
import jwt
from flask import current_app
from flask_socketio import emit, join_room, leave_room

from models import (
    get_conversations_collection,
    get_messages_collection,
    get_users_collection,
    message_to_dict,
    to_object_id,
    utcnow,
)


def _authenticate(auth_token):
    """Resolve a JWT to a user document, or None if invalid/expired."""
    if not auth_token:
        return None
    try:
        payload = jwt.decode(
            auth_token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
    except Exception:
        return None
    return get_users_collection(current_app.mongo).find_one(
        {"_id": to_object_id(payload.get("user_id"))}
    )


def _is_member(conversation, user_id):
    return bool(conversation) and user_id in conversation.get("participants", [])


def register_socket_handlers(socketio):
    @socketio.on("connect")
    def handle_connect(auth=None):
        token = (auth or {}).get("token") if isinstance(auth, dict) else None
        if not token and isinstance(auth, str):
            token = auth
        user = _authenticate(token)
        if not user:
            # Refuse the connection outright rather than letting anonymous
            # clients sit in the room registry.
            return False
        from flask import request as flask_request

        flask_request.environ["user"] = user
        emit("connected", {"user_id": str(user["_id"])})
        return True

    @socketio.on("join_conversation")
    def handle_join(data):
        from flask import request as flask_request

        user = flask_request.environ.get("user")
        if not user:
            emit("error", {"error": "unauthorized"})
            return

        conv_id = to_object_id((data or {}).get("conversation_id"))
        conv = get_conversations_collection(current_app.mongo).find_one({"_id": conv_id})
        if not _is_member(conv, user["_id"]):
            emit("error", {"error": "not a participant"})
            return

        join_room(str(conv_id))
        emit("joined", {"conversation_id": str(conv_id)})

    @socketio.on("leave_conversation")
    def handle_leave(data):
        conv_id = to_object_id((data or {}).get("conversation_id"))
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
        conv_id = to_object_id(data.get("conversation_id"))
        content = (data.get("content") or "").strip()
        if not content:
            emit("error", {"error": "content required"})
            return
        if len(content) > 4000:
            emit("error", {"error": "message too long"})
            return

        mongo = current_app.mongo
        conv_coll = get_conversations_collection(mongo)
        msg_coll = get_messages_collection(mongo)

        conv = conv_coll.find_one({"_id": conv_id})
        if not _is_member(conv, user["_id"]):
            emit("error", {"error": "not a participant"})
            return

        msg = {
            "sender": user["_id"],
            "conversation_id": conv_id,
            "content": content,
            "created_at": utcnow(),
            "read_by": [user["_id"]],
        }
        result = msg_coll.insert_one(msg)
        msg["_id"] = result.inserted_id
        conv_coll.update_one({"_id": conv_id}, {"$set": {"last_message_at": msg["created_at"]}})

        payload = message_to_dict(msg)
        emit("new_message", payload, to=str(conv_id))

    @socketio.on("typing")
    def handle_typing(data):
        from flask import request as flask_request

        user = flask_request.environ.get("user")
        if not user:
            return
        conv_id = to_object_id((data or {}).get("conversation_id"))
        conv = get_conversations_collection(current_app.mongo).find_one({"_id": conv_id})
        if not _is_member(conv, user["_id"]):
            return
        emit(
            "user_typing",
            {
                "conversation_id": str(conv_id),
                "user_id": str(user["_id"]),
                "name": user.get("name") or user.get("email"),
                "is_typing": bool((data or {}).get("is_typing", True)),
            },
            to=str(conv_id),
            include_self=False,
        )
