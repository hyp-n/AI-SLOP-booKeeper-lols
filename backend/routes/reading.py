from flask import Blueprint, request, jsonify, current_app
from models import get_books_collection, to_object_id, utcnow
from datetime import datetime, timezone
from bson.objectid import ObjectId

reading_bp = Blueprint("reading", __name__)


@reading_bp.route("/<book_id>", methods=["GET"])
def get_progress(book_id):
    """Get reading progress for a book."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    rp = book.get("reading_progress", {})
    if not rp:
        return jsonify({
            "book_id": book_id,
            "current_page": 0,
            "total_pages": None,
            "status": "want_to_read",
            "percentage": 0,
        })
    return jsonify({
        "current_page": rp.get("current_page", 0),
        "total_pages": rp.get("total_pages"),
        "status": rp.get("status", "want_to_read"),
        "percentage": rp.get("percentage", 0),
        "started_at": rp.get("started_at").isoformat() if rp.get("started_at") else None,
        "finished_at": rp.get("finished_at").isoformat() if rp.get("finished_at") else None,
        "updated_at": rp.get("updated_at").isoformat() if rp.get("updated_at") else None,
    })


@reading_bp.route("/<book_id>", methods=["PUT"])
def update_progress(book_id):
    """Update reading progress for a book."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    rp = book.get("reading_progress", {})

    if "current_page" in data:
        rp["current_page"] = data["current_page"]
    if "total_pages" in data:
        rp["total_pages"] = data["total_pages"]
    if "status" in data:
        old_status = rp.get("status", "want_to_read")
        rp["status"] = data["status"]

        now = datetime.now(timezone.utc)
        if data["status"] == "reading" and old_status != "reading":
            rp["started_at"] = now
        elif data["status"] == "finished":
            rp["finished_at"] = now
            rp["current_page"] = rp.get("total_pages") or rp.get("current_page", 0)
            rp["percentage"] = 100.0

    # Auto-calculate percentage
    total = rp.get("total_pages")
    if total and total > 0:
        rp["percentage"] = round((rp.get("current_page", 0) / total) * 100, 1)

    # Auto-update status based on percentage
    now = datetime.now(timezone.utc)
    if (rp.get("percentage") or 0) >= 100:
        rp["status"] = "finished"
        rp["finished_at"] = now
    elif rp.get("percentage", 0) > 0 and rp.get("status") == "want_to_read":
        rp["status"] = "reading"
        rp["started_at"] = now

    rp["updated_at"] = now
    books_coll.update_one({"_id": book["_id"]}, {"$set": {"reading_progress": rp}})

    return jsonify({
        "current_page": rp.get("current_page", 0),
        "total_pages": rp.get("total_pages"),
        "status": rp.get("status", "want_to_read"),
        "percentage": rp.get("percentage", 0),
        "started_at": rp.get("started_at").isoformat() if rp.get("started_at") else None,
        "finished_at": rp.get("finished_at").isoformat() if rp.get("finished_at") else None,
        "updated_at": rp.get("updated_at").isoformat() if rp.get("updated_at") else None,
    })


@reading_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get overall reading statistics."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    total_books = books_coll.count_documents({})
    want_to_read = books_coll.count_documents({"reading_progress.status": "want_to_read"})
    currently_reading = books_coll.count_documents({"reading_progress.status": "reading"})
    finished = books_coll.count_documents({"reading_progress.status": "finished"})

    # Sum current_page across all books
    pipeline = [
        {"$match": {"reading_progress.current_page": {"$gt": 0}}},
        {"$group": {"_id": None, "total": {"$sum": "$reading_progress.current_page"}}}
    ]
    result = list(books_coll.aggregate(pipeline))
    total_pages_read = result[0]["total"] if result else 0

    return jsonify({
        "total_books": total_books,
        "want_to_read": want_to_read,
        "currently_reading": currently_reading,
        "finished": finished,
        "total_pages_read": int(total_pages_read),
    })
