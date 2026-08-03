import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

FIREBASE_CREDENTIALS = Path(
    os.getenv("FIREBASE_CREDENTIALS", BASE_DIR / "firebase-credentials.json")
)
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "").strip()
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
