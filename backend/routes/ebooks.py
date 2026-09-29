from flask import Blueprint, request, jsonify
from models import db, Book, EbookSource
from services.annas_archive import search_annas_archive
from services.gutenberg import search_gutenberg

ebooks_bp = Blueprint("ebooks", __name__)


@ebooks_bp.route("/search", methods=["GET"])
def search_ebooks():
    """Search for ebook sources by query (ISBN or title)."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    if len(query) > 200:
        return jsonify({"error": "Query too long (max 200 characters)"}), 400

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


@ebooks_bp.errorhandler(400)
def ebook_bad_request(e):
    return jsonify({"error": "Bad request"}), 400


@ebooks_bp.route("/book/<book_id>", methods=["GET"])
def get_book_ebooks(book_id):
    """Get saved ebook sources for a book."""
    if not book_id or len(book_id) > 36:
        return jsonify({"error": "Invalid book ID"}), 400
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    sources = EbookSource.query.filter_by(book_id=book_id).all()
    return jsonify([{
        "source_name": s.source_name,
        "format": s.format,
        "external_url": s.external_url,
        "file_size": s.file_size,
    } for s in sources])


@ebooks_bp.route("/book/<book_id>", methods=["POST"])
def save_ebook_source(book_id):
    """Save an ebook source link for a book."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    external_url = data.get("external_url", "").strip()
    if not external_url:
        return jsonify({"error": "external_url is required"}), 400

    if not external_url.startswith(("http://", "https://")):
        return jsonify({"error": "external_url must be a valid URL"}), 400

    source = EbookSource(
        book_id=book_id,
        source_name=data.get("source_name", "unknown"),
        format=data.get("format", "epub"),
        external_url=external_url,
        file_size=data.get("file_size"),
    )

    db.session.add(source)
    db.session.commit()

    return jsonify({
        "source_name": source.source_name,
        "format": source.format,
        "external_url": source.external_url,
        "file_size": source.file_size,
    }), 201


@ebooks_bp.errorhandler(500)
def ebook_internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500