"""Application factory: builds and configures the Flask app."""
from flask import Flask, jsonify, send_from_directory

from backend.config import Config


def create_app():
    # Flask serves everything in /frontend directly (index.html, css, js...).
    app = Flask(
        __name__,
        static_folder=str(Config.FRONTEND_FOLDER),
        static_url_path="",
    )
    app.config.from_object(Config)

    @app.route("/")
    def home():
        return send_from_directory(Config.FRONTEND_FOLDER, "index.html")

    @app.route("/api/health")
    def health():
        # Simple endpoint to prove the backend is reachable from the browser.
        return jsonify(status="ok", message="Kiosk backend is running (demo mode)")

    # In Phase 1 we will register all blueprints (auth, account, cheque,
    # receipt, admin) here, once, so teammates never need to edit this file.

    return app