from flask import Blueprint, request, jsonify, current_app
from models import (
    get_books_collection, get_collections_collection,
    book_to_dict, collection_to_dict, to_object_id, utcnow
)
from bson.objectid import ObjectId

collections_bp = Blueprint("collections", __name__)


@collections_bp.route("/", methods=["GET"])
def list_collections():
    """List all collections."""
    mongo = current_app.mongo
    colls = get_collections_collection(mongo).find().sort("order_index", 1)
    return jsonify([collection_to_dict(c) for c in colls])


@collections_bp.route("/", methods=["POST"])
def create_collection():
    """Create a new collection."""
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    mongo = current_app.mongo
    coll_coll = get_collections_collection(mongo)

    # Get max order_index
    max_coll = coll_coll.find_one(sort=[("order_index", -1)])
    order_index = (max_coll["order_index"] + 1) if max_coll else 0

    coll = {
        "name": name,
        "description": data.get("description", ""),
        "order_index": order_index,
        "created_at": utcnow(),
    }

    result = coll_coll.insert_one(coll)
    coll["_id"] = result.inserted_id
    return jsonify(collection_to_dict(coll)), 201


@collections_bp.route("/<collection_id>", methods=["GET"])
def get_collection(collection_id):
    """Get a single collection with its books."""
    mongo = current_app.mongo
    coll_coll = get_collections_collection(mongo)

    coll = coll_coll.find_one({"_id": to_object_id(collection_id)})
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    result = collection_to_dict(coll)

    # Get books in this collection
    books = list(get_books_collection(mongo).find(
        {"collections.collection_id": coll["_id"]}
    ).sort("collections.order_index", 1))
    result["books"] = [book_to_dict(b) for b in books]

    return jsonify(result)


@collections_bp.route("/<collection_id>", methods=["PUT"])
def update_collection(collection_id):
    """Update collection name/description."""
    mongo = current_app.mongo
    coll_coll = get_collections_collection(mongo)

    coll = coll_coll.find_one({"_id": to_object_id(collection_id)})
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    data = request.get_json()
    update_fields = {}
    if "name" in data:
        update_fields["name"] = data["name"]
    if "description" in data:
        update_fields["description"] = data["description"]
    if "order_index" in data:
        update_fields["order_index"] = data["order_index"]

    if update_fields:
        coll_coll.update_one({"_id": coll["_id"]}, {"$set": update_fields})
        coll.update(update_fields)

    return jsonify(collection_to_dict(coll))


@collections_bp.route("/<collection_id>", methods=["DELETE"])
def delete_collection(collection_id):
    """Delete a collection (books stay in library)."""
    mongo = current_app.mongo
    coll_coll = get_collections_collection(mongo)

    coll_id = to_object_id(collection_id)
    coll = coll_coll.find_one({"_id": coll_id})
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    # Remove collection reference from books
    get_books_collection(mongo).update_many(
        {"collections.collection_id": coll_id},
        {"$pull": {"collections": {"collection_id": coll_id}}}
    )

    coll_coll.delete_one({"_id": coll_id})
    return jsonify({"message": "Collection deleted"}), 200


@collections_bp.route("/<collection_id>/books", methods=["POST"])
def add_book_to_collection(collection_id):
    """Add a book to a collection."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)
    coll_coll = get_collections_collection(mongo)

    coll = coll_coll.find_one({"_id": to_object_id(collection_id)})
    if not coll:
        return jsonify({"error": "Collection not found"}), 404

    data = request.get_json()
    book_id = data.get("book_id")

    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Check if already in collection
    for c in book.get("collections", []):
        if c.get("collection_id") == coll["_id"]:
            return jsonify({"error": "Book already in collection"}), 409

    # Get max order_index in this collection
    max_book = books_coll.find_one(
        {"collections.collection_id": coll["_id"]},
        sort=[("collections.order_index", -1)]
    )
    order_index = 0
    if max_book:
        for c in max_book.get("collections", []):
            if c.get("collection_id") == coll["_id"]:
                order_index = c.get("order_index", 0) + 1
                break

    books_coll.update_one(
        {"_id": book["_id"]},
        {"$push": {"collections": {"collection_id": coll["_id"], "order_index": order_index, "added_at": utcnow()}}}
    )

    book = books_coll.find_one({"_id": book["_id"]})
    return jsonify(book_to_dict(book)), 201


@collections_bp.route("/<collection_id>/books/<book_id>", methods=["DELETE"])
def remove_book_from_collection(collection_id, book_id):
    """Remove a book from a collection."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    book = books_coll.find_one({"_id": to_object_id(book_id)})
    if not book:
        return jsonify({"error": "Book not found"}), 404

    books_coll.update_one(
        {"_id": book["_id"]},
        {"$pull": {"collections": {"collection_id": to_object_id(collection_id)}}}
    )

    return jsonify({"message": "Book removed from collection"}), 200


@collections_bp.route("/<collection_id>/reorder", methods=["PUT"])
def reorder_books(collection_id):
    """Reorder books within a collection."""
    mongo = current_app.mongo
    books_coll = get_books_collection(mongo)

    data = request.get_json()
    book_ids = data.get("book_ids", [])

    for index, book_id in enumerate(book_ids):
        books_coll.update_one(
            {"_id": to_object_id(book_id), "collections.collection_id": to_object_id(collection_id)},
            {"$set": {"collections.$.order_index": index}}
        )

    return jsonify({"message": "Order updated"}), 200
