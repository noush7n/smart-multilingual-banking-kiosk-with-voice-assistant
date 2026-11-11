"""Application factory: builds and configures the Flask app."""
import importlib
import pkgutil

from flask import Flask, jsonify, send_from_directory

from backend import db, routes
from backend.config import Config


def create_app():
    app = Flask(
        __name__,
        static_folder=str(Config.FRONTEND_FOLDER),
        static_url_path="",
    )
    app.config.from_object(Config)
    db.init_app(app)

    @app.route("/")
    def home():
        return send_from_directory(Config.FRONTEND_FOLDER, "index.html")

    @app.route("/api/health")
    def health():
        return jsonify(status="ok", message="Kiosk backend is running")

    # Register every file in backend/routes/ that defines a variable named "bp"
    for module_info in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"backend.routes.{module_info.name}")
        if hasattr(module, "bp"):
            app.register_blueprint(module.bp)

    return app