"""PDF extraction helpers with OCR fallback for uploaded documents."""

import pdfplumber
from functools import lru_cache

from config import OCR_LANGUAGES
from logger_config import logger

MAX_OCR_PAGES = 5


@lru_cache(maxsize=32)
def cached_pdf_text(file_path: str) -> str:
    '''Extract text from a PDF file, caching the result for performance.'''
    return extract_text_from_pdf(file_path)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF using pdfplumber."""
    parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
    return "\n".join(parts).strip()


def extract_text_with_ocr_fallback(file_path: str) -> str:
    """Extract text with OCR fallback if normal extraction yields little content."""
    text = cached_pdf_text(file_path)

    if len(text) > 100:
        return text

    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        return text

    try:
        # Prevent memory exhaustion by capping the number of pages converted
        images = convert_from_path(file_path, dpi=200, first_page=1, last_page=MAX_OCR_PAGES)
        ocr_parts = []

        for img in images:
            page_text = pytesseract.image_to_string(img, lang=OCR_LANGUAGES)
            if page_text:
                ocr_parts.append(page_text)

        ocr_text = "\n".join(ocr_parts).strip() or text
        logger.info("OCR fallback used for file='%s' extracted=%s chars", file_path, len(ocr_text))
        return ocr_text

    except Exception:
        logger.exception("OCR processing failed.")
        return text


def is_ocr_available() -> bool:
    """Check if OCR dependencies are available (pytesseract and pdf2image)."""
    try:
        import pytesseract
        import pdf2image
        return True
    except ImportError:
        return False