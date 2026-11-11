"""Central configuration for the kiosk app."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    # Used to sign session cookies. This is a DEMO value only.
    # Real applications load this from an environment variable.
    SECRET_KEY = os.environ.get("KIOSK_SECRET_KEY", "demo-only-change-me")

    DATABASE_PATH = BASE_DIR / "database" / "kiosk.db"
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    FRONTEND_FOLDER = BASE_DIR / "frontend"

    # Reject uploads larger than 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024