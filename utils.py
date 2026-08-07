"""Utility helpers for validating uploaded files in the SmartGovAI app."""

import urllib.parse
from typing import Any, Dict, Optional, Tuple

import pdfplumber
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_PDF_PAGES
from logger_config import logger


def allowed_file(
    file: FileStorage,
) -> Tuple[bool, str]:
    """
    Validate uploaded PDF files.

    Returns:
        (success, message_or_filename)
    """
    if not file:
        return False, "No file uploaded."
    if not file.filename:
        return False, "No file selected."
    filename = secure_filename(file.filename)
    if "." not in filename:
        return False, "Invalid filename."
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False, "Only PDF files are supported."
    if file.mimetype not in ALLOWED_MIME_TYPES:
        return False, "Invalid file type."
    return True, filename


def safe_url(value: Optional[str]) -> str:
    """Return *value* only if its scheme is http or https, otherwise empty string.

    This prevents ``javascript:``, ``data:``, and other dangerous URI
    schemes from being injected into ``href`` attributes.
    """
    if not value:
        return ""
    parsed = urllib.parse.urlparse(value)
    return value if parsed.scheme in {"http", "https"} else ""


def validate_pdf_content(file_path: str) -> Tuple[bool, str]:
    """Validate a saved PDF file by checking magic bytes and page count.

    This provides **basic** PDF hardening:
    - Magic-byte check (%PDF header)
    - Page-count limit (MAX_PDF_PAGES)

    **Not implemented** (deferred):
    - Decompressed-size / zip-bomb protection
    - Hard parse timeout (platform-dependent; size/page limits serve as proxy)

    Returns:
        (valid, error_message)
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
        if not header.startswith(b"%PDF"):
            return False, "Uploaded file is not a valid PDF."
    except OSError as e:
        logger.warning("Failed to read PDF header from '%s': %s", file_path, e)
        return False, "Could not read uploaded file."

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            if page_count > MAX_PDF_PAGES:
                return False, f"PDF has {page_count} pages (limit is {MAX_PDF_PAGES})."
    except Exception as e:
        logger.warning("Failed to open/parse PDF '%s': %s", file_path, e)
        return False, "Uploaded PDF could not be parsed."

    return True, ""

