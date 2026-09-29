import os

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from config import DATABASE_URL, SECRET_KEY, ALLOWED_ORIGINS, FLASK_DEBUG
from models import db

socketio = SocketIO()


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist"
        ),
        static_url_path="",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["JSON_SORT_KEYS"] = False

    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})
    db.init_app(app)

    # Function-level imports avoid circular imports between blueprints
    from routes.books import books_bp
    from routes.collections import collections_bp
    from routes.ebooks import ebooks_bp
    from routes.reading import reading_bp
    from routes.auth import auth_bp
    from routes.social import social_bp
    from routes.messages import messages_bp

    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(collections_bp, url_prefix="/api/collections")
    app.register_blueprint(ebooks_bp, url_prefix="/api/ebooks")
    app.register_blueprint(reading_bp, url_prefix="/api/reading")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(social_bp, url_prefix="/api/social")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")

    from routes.socket_events import register_socket_handlers

    socketio.init_app(
        app,
        cors_allowed_origins=ALLOWED_ORIGINS,
        async_mode="threading",
    )
    register_socket_handlers(socketio)

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                "Could not create database tables (database may not be available): %s", e
            )

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/")
    def serve_frontend():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        full = os.path.join(app.static_folder, path)
        if os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    socketio.run(
        application,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=FLASK_DEBUG,
        allow_unsafe_werkzeug=True,
    )
