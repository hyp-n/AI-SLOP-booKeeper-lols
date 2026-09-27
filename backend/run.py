import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_socketio import SocketIO

from config import MONGODB_URI, SECRET_KEY, ALLOWED_ORIGINS, FLASK_DEBUG

mongo = PyMongo()
socketio = SocketIO()


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist"
        ),
        static_url_path="",
    )
    app.config["MONGO_URI"] = MONGODB_URI
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["JSON_SORT_KEYS"] = False

    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})
    mongo.init_app(app)
    app.mongo = mongo

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

    @app.route("/")
    def serve_frontend():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        full = os.path.join(app.static_folder, path)
        if os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        # SPA fallback: unknown paths are client-side routes
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
