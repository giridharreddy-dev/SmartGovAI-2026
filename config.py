import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

SCHEMES_PATH = os.path.join(BASE_DIR, "schemes_complex.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
STATIC_DIR = os.path.join(BASE_DIR, "static")

ALLOWED_EXTENSIONS = {"pdf"}
ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024

MODEL_NAME = "gemini-2.5-flash"

OCR_LANGUAGES = "tel+eng"
VOICE_LANGUAGE = "te"

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
DEBUG_MODE = False

DB_PATH = os.path.join(BASE_DIR, "feedback.db")