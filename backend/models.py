import uuid
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


def generate_id():
    return str(uuid.uuid4())


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    isbn = db.Column(db.String(20), nullable=True)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(500), nullable=True)
    cover_url = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    publisher = db.Column(db.String(500), nullable=True)
    published_date = db.Column(db.String(50), nullable=True)
    page_count = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    # Reading progress (embedded)
    reading_status = db.Column(db.String(20), default="want_to_read")
    current_page = db.Column(db.Integer, default=0)
    reading_percentage = db.Column(db.Float, default=0.0)
    reading_started_at = db.Column(db.DateTime, nullable=True)
    reading_finished_at = db.Column(db.DateTime, nullable=True)
    reading_updated_at = db.Column(db.DateTime, default=utcnow)

    # Relationships
    collections = db.relationship("CollectionBook", back_populates="book", cascade="all, delete-orphan")
    ebook_sources = db.relationship("EbookSource", back_populates="book", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "cover_url": self.cover_url,
            "description": self.description,
            "publisher": self.publisher,
            "published_date": self.published_date,
            "page_count": self.page_count,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "reading_status": self.reading_status,
            "current_page": self.current_page,
            "reading_percentage": self.reading_percentage,
        }


class BookCollection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)

    # Relationships
    books = db.relationship("CollectionBook", back_populates="collection", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "order_index": self.order_index,
            "book_count": len(self.books),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CollectionBook(db.Model):
    __tablename__ = "collection_books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    collection_id = db.Column(db.String(36), db.ForeignKey("collections.id"), nullable=False)
    book_id = db.Column(db.String(36), db.ForeignKey("books.id"), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    added_at = db.Column(db.DateTime, default=utcnow)

    # Relationships
    collection = db.relationship("BookCollection", back_populates="books")
    book = db.relationship("Book", back_populates="collections")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(200), nullable=True)
    avatar_url = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    currently_reading = db.Column(db.String(36), nullable=True)
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "currently_reading": self.currently_reading,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FriendRequest(db.Model):
    __tablename__ = "friend_requests"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    sender_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=utcnow)


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    is_group = db.Column(db.Boolean, default=False)
    group_name = db.Column(db.String(200), nullable=True)
    group_admin = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    last_message_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    participants = db.relationship("ConversationParticipant", back_populates="conversation", cascade="all, delete-orphan")
    messages = db.relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "is_group": self.is_group,
            "group_name": self.group_name,
            "group_admin": self.group_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
        }


class ConversationParticipant(db.Model):
    __tablename__ = "conversation_participants"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey("conversations.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    # Relationships
    conversation = db.relationship("Conversation", back_populates="participants")


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    sender_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    conversation_id = db.Column(db.String(36), db.ForeignKey("conversations.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    read_by = db.Column(db.JSON, default=list)

    # Relationships
    conversation = db.relationship("Conversation", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender_id,
            "conversation_id": self.conversation_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_by": self.read_by or [],
        }


class EbookSource(db.Model):
    __tablename__ = "ebook_sources"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.String(36), db.ForeignKey("books.id"), nullable=False)
    source_name = db.Column(db.String(200))
    format = db.Column(db.String(50))
    external_url = db.Column(db.Text)
    file_size = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    # Relationships
    book = db.relationship("Book", back_populates="ebook_sources")