from flask import Blueprint, request, jsonify
from models import db, Book
from datetime import datetime, timezone

reading_bp = Blueprint("reading", __name__)


@reading_bp.route("/<book_id>", methods=["GET"])
def get_progress(book_id):
    """Get reading progress for a book."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({
        "current_page": book.current_page,
        "total_pages": book.page_count,
        "status": book.reading_status,
        "percentage": book.reading_percentage,
        "started_at": book.reading_started_at.isoformat() if book.reading_started_at else None,
        "finished_at": book.reading_finished_at.isoformat() if book.reading_finished_at else None,
        "updated_at": book.reading_updated_at.isoformat() if book.reading_updated_at else None,
    })


@reading_bp.errorhandler(404)
def reading_not_found(e):
    return jsonify({"error": "Reading progress not found"}), 404


@reading_bp.route("/<book_id>", methods=["PUT"])
def update_progress(book_id):
    """Update reading progress for a book."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    if "current_page" in data and "total_pages" in data:
        if data["current_page"] > data["total_pages"]:
            return jsonify({"error": "current_page cannot be greater than total_pages"}), 400

    if "current_page" in data:
        page = data["current_page"]
        if not isinstance(page, int) or page < 0:
            return jsonify({"error": "current_page must be a non-negative integer"}), 400
        book.current_page = page
    if "total_pages" in data:
        total = data["total_pages"]
        if not isinstance(total, int) or total < 0:
            return jsonify({"error": "total_pages must be a non-negative integer"}), 400
        book.page_count = total
    if "status" in data:
        old_status = book.reading_status
        book.reading_status = data["status"]

        now = datetime.now(timezone.utc)
        if data["status"] == "reading" and old_status != "reading":
            book.reading_started_at = now
        elif data["status"] == "finished":
            book.reading_finished_at = now
            book.current_page = book.page_count or book.current_page
            book.reading_percentage = 100.0
        elif data["status"] not in ("want_to_read", "reading", "finished"):
            return jsonify({"error": "Invalid status. Must be one of: want_to_read, reading, finished"}), 400

    # Auto-calculate percentage
    total = book.page_count
    if total and total > 0:
        book.reading_percentage = round((book.current_page / total) * 100, 1)

    # Auto-update status based on percentage
    now = datetime.now(timezone.utc)
    if (book.reading_percentage or 0) >= 100:
        book.reading_status = "finished"
        book.reading_finished_at = now
    elif (book.reading_percentage or 0) > 0 and book.reading_status == "want_to_read":
        book.reading_status = "reading"
        book.reading_started_at = now

    book.reading_updated_at = now
    db.session.commit()

    return jsonify({
        "current_page": book.current_page,
        "total_pages": book.page_count,
        "status": book.reading_status,
        "percentage": book.reading_percentage,
        "started_at": book.reading_started_at.isoformat() if book.reading_started_at else None,
        "finished_at": book.reading_finished_at.isoformat() if book.reading_finished_at else None,
        "updated_at": book.reading_updated_at.isoformat() if book.reading_updated_at else None,
    })


@reading_bp.errorhandler(400)
def reading_bad_request(e):
    return jsonify({"error": "Bad request"}), 400


@reading_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get overall reading statistics."""
    total_books = Book.query.count()
    want_to_read = Book.query.filter_by(reading_status="want_to_read").count()
    currently_reading = Book.query.filter_by(reading_status="reading").count()
    finished = Book.query.filter_by(reading_status="finished").count()

    # Sum current_page across all books with progress
    total_pages_read = (
        Book.query.filter(Book.current_page > 0)
        .with_entities(db.func.sum(Book.current_page))
        .scalar()
    ) or 0

    return jsonify({
        "total_books": total_books,
        "want_to_read": want_to_read,
        "currently_reading": currently_reading,
        "finished": finished,
        "total_pages_read": int(total_pages_read),
    })


@reading_bp.errorhandler(500)
def reading_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500