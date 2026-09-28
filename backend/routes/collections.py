from flask import Blueprint, request, jsonify
from models import db, Book, BookCollection, CollectionBook

collections_bp = Blueprint("collections", __name__)


@collections_bp.route("/", methods=["GET"])
def list_collections():
    """List all collections."""
    colls = BookCollection.query.order_by(BookCollection.order_index.asc()).all()
    return jsonify([c.to_dict() for c in colls])


@collections_bp.route("/", methods=["POST"])
def create_collection():
    """Create a new collection."""
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    max_coll = BookCollection.query.order_by(BookCollection.order_index.desc()).first()
    order_index = (max_coll.order_index + 1) if max_coll else 0

    coll = BookCollection(
        name=name,
        description=data.get("description", ""),
        order_index=order_index,
    )

    db.session.add(coll)
    db.session.commit()
    return jsonify(coll.to_dict()), 201


@collections_bp.route("/<collection_id>", methods=["GET"])
def get_collection(collection_id):
    """Get a single collection with its books."""
    coll = BookCollection.query.get(collection_id)
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    result = coll.to_dict()

    # Get books in this collection, ordered by their order_index in the collection
    books = (
        Book.query.join(CollectionBook, Book.id == CollectionBook.book_id)
        .filter(CollectionBook.collection_id == collection_id)
        .order_by(CollectionBook.order_index.asc())
        .all()
    )
    result["books"] = [b.to_dict() for b in books]

    return jsonify(result)


@collections_bp.route("/<collection_id>", methods=["PUT"])
def update_collection(collection_id):
    """Update collection name/description."""
    coll = BookCollection.query.get(collection_id)
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    data = request.get_json()
    if "name" in data:
        coll.name = data["name"]
    if "description" in data:
        coll.description = data["description"]
    if "order_index" in data:
        coll.order_index = data["order_index"]

    db.session.commit()
    return jsonify(coll.to_dict())


@collections_bp.route("/<collection_id>", methods=["DELETE"])
def delete_collection(collection_id):
    """Delete a collection (books stay in library)."""
    coll = BookCollection.query.get(collection_id)
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    db.session.delete(coll)
    db.session.commit()
    return jsonify({"message": "Collection deleted"}), 200


@collections_bp.route("/<collection_id>/books", methods=["POST"])
def add_book_to_collection(collection_id):
    """Add a book to a collection."""
    coll = BookCollection.query.get(collection_id)
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    data = request.get_json()
    book_id = data.get("book_id")

    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Check if already in collection
    existing = CollectionBook.query.filter_by(
        collection_id=collection_id, book_id=book_id
    ).first()
    if existing:
        return jsonify({"error": "Book already in collection"}), 409

    # Get max order_index in this collection
    max_cb = (
        CollectionBook.query.filter_by(collection_id=collection_id)
        .order_by(CollectionBook.order_index.desc())
        .first()
    )
    order_index = (max_cb.order_index + 1) if max_cb else 0

    cb = CollectionBook(
        collection_id=collection_id,
        book_id=book_id,
        order_index=order_index,
    )

    db.session.add(cb)
    db.session.commit()

    book = Book.query.get(book_id)
    return jsonify(book.to_dict()), 201


@collections_bp.route("/<collection_id>/books/<book_id>", methods=["DELETE"])
def remove_book_from_collection(collection_id, book_id):
    """Remove a book from a collection."""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    cb = CollectionBook.query.filter_by(
        collection_id=collection_id, book_id=book_id
    ).first()

    if cb:
        db.session.delete(cb)
        db.session.commit()

    return jsonify({"message": "Book removed from collection"}), 200


@collections_bp.route("/<collection_id>/reorder", methods=["PUT"])
def reorder_books(collection_id):
    """Reorder books within a collection."""
    data = request.get_json()
    book_ids = data.get("book_ids", [])

    for index, book_id in enumerate(book_ids):
        cb = CollectionBook.query.filter_by(
            collection_id=collection_id, book_id=book_id
        ).first()
        if cb:
            cb.order_index = index

    db.session.commit()
    return jsonify({"message": "Order updated"}), 200