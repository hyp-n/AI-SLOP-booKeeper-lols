from flask import Blueprint, request, jsonify, current_app
from models import (
    get_books_collection, book_to_dict, to_object_id, utcnow
)
from services.openlibrary import lookup_isbn, search_books
from bson.objectid import ObjectId

books_bp = Blueprint("books", __name__)


@books_bp.route("/", methods=["GET"])
def list_books():
    """List all books in the library."""
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    sort = request.args.get("sort", "created_at")

    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    filter_query = {}
    if query:
        filter_query["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"author": {"$regex": query, "$options": "i"}},
            {"isbn": {"$regex": query, "$options": "i"}},
        ]
    if status:
        filter_query["reading_progress.status"] = status

    sort_field = {
        "title": ("title", 1),
        "author": ("author", 1),
        "created_at": ("created_at", -1),
    }.get(sort, ("created_at", -1))

    books = list(books_coll.find(filter_query).sort(*sort_field))
    return jsonify([book_to_dict(b) for b in books])


@books_bp.route("/lookup/<isbn>", methods=["GET"])
def lookup(isbn):
    """Look up a book by ISBN via OpenLibrary."""
    result = lookup_isbn(isbn)
    if result:
        return jsonify(result)
    return jsonify({"error": "Book not found"}), 404


@books_bp.route("/search", methods=["GET"])
def search():
    """Search OpenLibrary by query string."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    results = search_books(query)
    return jsonify(results)


@books_bp.route("/", methods=["POST"])
def add_book():
    """Add a book to the library."""
    data = request.get_json()

    isbn = (data.get("isbn") or "").strip()
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    # Check for duplicate by ISBN
    if isbn:
        existing = books_coll.find_one({"isbn": isbn})
        if existing:
            return jsonify({"error": "Book with this ISBN already exists", "book": book_to_dict(existing)}), 409

    book = {
        "isbn": isbn if isbn else None,
        "title": title,
        "author": author,
        "cover_url": data.get("cover_url") or None,
        "description": data.get("description") or None,
        "publisher": data.get("publisher") or None,
        "published_date": data.get("published_date") or None,
        "page_count": data.get("page_count") or None,
        "language": data.get("language") or None,
        "created_at": utcnow(),
        "reading_progress": {
            "current_page": 0,
            "total_pages": data.get("page_count"),
            "status": "want_to_read",
            "percentage": 0.0,
            "started_at": None,
            "finished_at": None,
            "updated_at": utcnow(),
        },
        "ebook_sources": [],
        "collections": [],
    }

    result = books_coll.insert_one(book)
    book["_id"] = result.inserted_id
    return jsonify(book_to_dict(book)), 201


@books_bp.route("/add-by-isbn/<isbn>", methods=["POST"])
def add_by_isbn(isbn):
    """Look up ISBN and add to library in one step."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    # Check if already in library
    existing = books_coll.find_one({"isbn": isbn})
    if existing:
        return jsonify({"error": "Book already in library", "book": book_to_dict(existing)}), 409

    result = lookup_isbn(isbn)
    if not result:
        return jsonify({"error": "Could not find book with this ISBN"}), 404

    # Filter result to only valid Book fields
    valid_fields = {"isbn", "title", "author", "cover_url", "description", "publisher", "published_date", "page_count", "language"}
    filtered = {k: v for k, v in result.items() if k in valid_fields}

    book = {
        **filtered,
        "created_at": utcnow(),
        "reading_progress": {
            "current_page": 0,
            "total_pages": filtered.get("page_count"),
            "status": "want_to_read",
            "percentage": 0.0,
            "started_at": None,
            "finished_at": None,
            "updated_at": utcnow(),
        },
        "ebook_sources": [],
        "collections": [],
    }

    try:
        result = books_coll.insert_one(book)
        book["_id"] = result.inserted_id
        return jsonify(book_to_dict(book)), 201
    except Exception as e:
        if "duplicate" in str(e).lower() or "E11000" in str(e):
            return jsonify({"error": "Book with this ISBN already exists"}), 409
        raise


@books_bp.route("/<book_id>", methods=["GET"])
def get_book(book_id):
    """Get a single book's details."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book_to_dict(book))


@books_bp.route("/<book_id>", methods=["PUT"])
def update_book(book_id):
    """Update book metadata."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    update_fields = {}
    for field in ["title", "author", "cover_url", "description", "publisher", "published_date", "page_count", "language"]:
        if field in data:
            update_fields[field] = data[field]

    if update_fields:
        books_coll.update_one({"_id": book["_id"]}, {"$set": update_fields})
        book.update(update_fields)

    return jsonify(book_to_dict(book))


@books_bp.route("/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    """Remove a book from the library."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    result = books_coll.delete_one({"_id": to_object_id(book_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted"}), 200
