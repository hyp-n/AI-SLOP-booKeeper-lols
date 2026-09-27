from flask import Blueprint, request, jsonify, current_app
from models import get_books_collection, to_object_id, utcnow
from services.annas_archive import search_annas_archive
from services.gutenberg import search_gutenberg

ebooks_bp = Blueprint("ebooks", __name__)


@ebooks_bp.route("/search", methods=["GET"])
def search_ebooks():
    """Search for ebook sources by query (ISBN or title)."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = []

    # Search Anna's Archive
    anna_results = search_annas_archive(query)
    for r in anna_results:
        results.append({
            "source_name": r.get("source_name", "Anna's Archive"),
            "format": r.get("format", "epub"),
            "external_url": r.get("external_url", ""),
            "file_size": r.get("format_info", ""),
            "cover_url": r.get("cover_url"),
        })

    # Search Project Gutenberg
    gutenberg_results = search_gutenberg(query)
    for r in gutenberg_results:
        if r.get("epub_url"):
            fmt = "epub"
        elif r.get("pdf_url"):
            fmt = "pdf"
        else:
            fmt = "epub"
        results.append({
            "source_name": r.get("source_name", "Project Gutenberg"),
            "format": fmt,
            "external_url": r.get("external_url", ""),
            "file_size": "",
            "cover_url": r.get("cover_url"),
        })

    return jsonify(results)


@ebooks_bp.route("/book/<book_id>", methods=["GET"])
def get_book_ebooks(book_id):
    """Get saved ebook sources for a book."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    sources = book.get("ebook_sources", [])
    return jsonify([{
        "source_name": s.get("source_name", ""),
        "format": s.get("format", ""),
        "external_url": s.get("external_url", ""),
        "file_size": s.get("file_size"),
    } for s in sources])


@ebooks_bp.route("/book/<book_id>", methods=["POST"])
def save_ebook_source(book_id):
    """Save an ebook source link for a book."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    source = {
        "source_name": data.get("source_name", "unknown"),
        "format": data.get("format", "epub"),
        "external_url": data.get("external_url", ""),
        "file_size": data.get("file_size"),
        "created_at": utcnow(),
    }

    books_coll.update_one(
        {"_id": book["_id"]},
        {"$push": {"ebook_sources": source}}
    )

    return jsonify(source), 201
