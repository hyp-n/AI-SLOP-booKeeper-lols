from datetime import datetime, timezone
from bson.objectid import ObjectId


def utcnow():
    return datetime.now(timezone.utc)


def to_object_id(id_str):
    """Convert string to ObjectId, return None if invalid."""
    if not id_str:
        return None
    try:
        return ObjectId(id_str)
    except:
        return None


def serialize_id(doc):
    """Convert _id to id string in a document dict."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


# Book collection name
BOOKS_COLLECTION = "books"
COLLECTIONS_COLLECTION = "collections"
USERS_COLLECTION = "users"
FRIEND_REQUESTS_COLLECTION = "friend_requests"
MESSAGES_COLLECTION = "messages"
CONVERSATIONS_COLLECTION = "conversations"


def get_books_collection(mongo):
    return mongo.db[BOOKS_COLLECTION]


def get_collections_collection(mongo):
    return mongo.db[COLLECTIONS_COLLECTION]


def get_users_collection(mongo):
    return mongo.db[USERS_COLLECTION]


def get_friend_requests_collection(mongo):
    return mongo.db[FRIEND_REQUESTS_COLLECTION]


def get_messages_collection(mongo):
    return mongo.db[MESSAGES_COLLECTION]


def get_conversations_collection(mongo):
    return mongo.db[CONVERSATIONS_COLLECTION]


def book_to_dict(book):
    """Convert a Book document to a JSON-serializable dict."""
    if not book:
        return None
    book_id = str(book.get("_id", ""))
    rp = book.get("reading_progress", {}) or {}
    return {
        "id": book_id,
        "isbn": book.get("isbn"),
        "title": book.get("title", ""),
        "author": book.get("author"),
        "cover_url": book.get("cover_url"),
        "description": book.get("description"),
        "publisher": book.get("publisher"),
        "published_date": book.get("published_date"),
        "page_count": book.get("page_count"),
        "language": book.get("language"),
        "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
        "reading_status": rp.get("status", "want_to_read"),
        "current_page": rp.get("current_page", 0),
        "reading_percentage": rp.get("percentage", 0),
    }


def collection_to_dict(coll):
    """Convert a Collection document to a JSON-serializable dict."""
    if not coll:
        return None
    return {
        "id": str(coll.get("_id", "")),
        "name": coll.get("name", ""),
        "description": coll.get("description", ""),
        "order_index": coll.get("order_index", 0),
        "book_count": coll.get("book_count", 0),
        "created_at": coll.get("created_at").isoformat() if coll.get("created_at") else None,
    }


def user_to_dict(user):
    """Convert a User document to a JSON-serializable dict."""
    if not user:
        return None
    return {
        "id": str(user.get("_id", "")),
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "avatar_url": user.get("avatar_url"),
        "bio": user.get("bio", ""),
        "currently_reading": str(user.get("currently_reading")) if user.get("currently_reading") else None,
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
    }


def message_to_dict(msg):
    """Convert a Message document to a JSON-serializable dict."""
    if not msg:
        return None
    return {
        "id": str(msg.get("_id", "")),
        "sender": str(msg.get("sender", "")),
        "conversation_id": str(msg.get("conversation_id", "")),
        "content": msg.get("content", ""),
        "created_at": msg.get("created_at").isoformat() if msg.get("created_at") else None,
        "read_by": [str(uid) for uid in msg.get("read_by", [])],
    }


def conversation_to_dict(conv):
    """Convert a Conversation document to a JSON-serializable dict."""
    if not conv:
        return None
    return {
        "id": str(conv.get("_id", "")),
        "participants": [str(p) for p in conv.get("participants", [])],
        "is_group": conv.get("is_group", False),
        "group_name": conv.get("group_name"),
        "group_admin": str(conv.get("group_admin")) if conv.get("group_admin") else None,
        "created_at": conv.get("created_at").isoformat() if conv.get("created_at") else None,
        "last_message_at": conv.get("last_message_at").isoformat() if conv.get("last_message_at") else None,
    }
