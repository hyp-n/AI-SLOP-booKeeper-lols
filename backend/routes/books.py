from flask import Blueprint, request, jsonify
from models import db, Book, CollectionBook
from services.openlibrary import lookup_isbn, search_books

books_bp = Blueprint("books", __name__)


@books_bp.route("/", methods=["GET"])
def list_books():
    """List all books in the library."""
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    sort = request.args.get("sort", "created_at")

    q = Book.query

    if query:
        like = f"%{query}%"
        q = q.filter(
            db.or_(
                Book.title.ilike(like),
                Book.author.ilike(like),
                Book.isbn.ilike(like),
            )
        )

    if status:
        q = q.filter(Book.reading_status == status)

    if sort == "title":
        q = q.order_by(Book.title.asc())
    elif sort == "author":
        q = q.order_by(Book.author.asc())
    else:
        q = q.order_by(Book.created_at.desc())

    books = q.all()
    return jsonify([b.to_dict() for b in books])


@books_bp.route("/lookup/<isbn>", methods=["GET"])
def lookup(isbn):
    """Look up a book by ISBN via OpenLibrary."""
    if not isbn or len(isbn) > 20:
        return jsonify({"error": "Invalid ISBN"}), 400
    result = lookup_isbn(isbn)
    if result:
        return jsonify(result)
    return jsonify({"error": "Book not found"}), 404


@books_bp.route("/search", methods=["GET"])
def search():
    """Search OpenLibrary by query string."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    if len(query) > 200:
        return jsonify({"error": "Query too long (max 200 characters)"}), 400
    results = search_books(query)
    return jsonify(results)


@books_bp.route("/", methods=["POST"])
def add_book():
    """Add a book to the library."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    isbn = (data.get("isbn") or "").strip()
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    if len(title) > 500:
        return jsonify({"error": "Title must be 500 characters or less"}), 400

    if isbn and len(isbn) > 20:
        return jsonify({"error": "ISBN must be 20 characters or less"}), 400

    # Check for duplicate by ISBN
    if isbn:
        existing = Book.query.filter_by(isbn=isbn).first()
        if existing:
            return jsonify({"error": "Book with this ISBN already exists", "book": existing.to_dict()}), 409

    book = Book(
        isbn=isbn if isbn else None,
        title=title,
        author=author,
        cover_url=data.get("cover_url") or None,
        description=data.get("description") or None,
        publisher=data.get("publisher") or None,
        published_date=data.get("published_date") or None,
        page_count=data.get("page_count") or None,
        language=data.get("language") or None,
        reading_status="want_to_read",
        current_page=0,
        reading_percentage=0.0,
    )

    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@books_bp.route("/add-by-isbn/<isbn>", methods=["POST"])
def add_by_isbn(isbn):
    """Look up ISBN and add to library in one step."""
    if not isbn or len(isbn) > 20:
        return jsonify({"error": "Invalid ISBN"}), 400

    # Check if already in library
    existing = Book.query.filter_by(isbn=isbn).first()
    if existing:
        return jsonify({"error": "Book already in library", "book": existing.to_dict()}), 409

    result = lookup_isbn(isbn)
    if not result:
        return jsonify({"error": "Could not find book with this ISBN"}), 404

    # Filter result to only valid Book fields
    valid_fields = {"isbn", "title", "author", "cover_url", "description", "publisher", "published_date", "page_count", "language"}
    filtered = {k: v for k, v in result.items() if k in valid_fields}

    book = Book(
        **filtered,
        reading_status="want_to_read",
        current_page=0,
        reading_percentage=0.0,
    )

    try:
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return jsonify({"error": "Book with this ISBN already exists"}), 409
        raise


@books_bp.route("/<book_id>", methods=["GET"])
def get_book(book_id):
    """Get a single book's details."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict())


@books_bp.errorhandler(404)
def book_not_found(e):
    return jsonify({"error": "Book not found"}), 404


@books_bp.errorhandler(500)
def book_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


@books_bp.route("/<book_id>", methods=["PUT"])
def update_book(book_id):
    """Update book metadata."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    for field in ["title", "author", "cover_url", "description", "publisher", "published_date", "page_count", "language"]:
        if field in data:
            setattr(book, field, data[field])

    db.session.commit()
    return jsonify(book.to_dict())


@books_bp.route("/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    """Remove a book from the library."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200


@books_bp.errorhandler(500)
def book_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500