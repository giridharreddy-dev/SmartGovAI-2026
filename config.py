import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

SCHEMES_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio", "dynamic")

ALLOWED_EXTENSIONS = {"pdf"}
ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "50"))

MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash")

# Gemini retry configuration
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
GEMINI_RETRY_BASE_DELAY = float(os.getenv("GEMINI_RETRY_BASE_DELAY", "2.0"))
GEMINI_RETRY_MAX_DELAY = float(os.getenv("GEMINI_RETRY_MAX_DELAY", "10.0"))
OCR_LANGUAGES = "tel+eng"
VOICE_LANGUAGE = "te"

SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "0").lower() in {"1", "true", "yes"}

DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "feedback.db"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")