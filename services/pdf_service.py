"""PDF extraction helpers with OCR fallback for uploaded documents."""

from functools import lru_cache

import pdfplumber

from config import MAX_EXTRACTED_CHARS, MAX_PDF_PAGES, OCR_LANGUAGES
from logger_config import logger

MAX_OCR_PAGES = 5


def limit_text_length(text: str, limit: int = MAX_EXTRACTED_CHARS) -> str:
    """Truncate extracted text to ``limit`` characters.

    Bounds the size of the Gemini prompt and worker memory regardless of how
    many pages a PDF declares, preventing resource and cost amplification.
    """
    if limit <= 0 or len(text) <= limit:
        return text
    truncated = text[:limit]
    logger.warning("Extracted text truncated to %d chars (was %d).", limit, len(text))
    return truncated


@lru_cache(maxsize=32)
def cached_pdf_text(file_path: str) -> str:
    '''Extract text from a PDF file, caching the result for performance.'''
    return extract_text_from_pdf(file_path)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF using pdfplumber.

    Stops after MAX_PDF_PAGES pages so a crafted page-bomb PDF cannot drive
    unbounded CPU/memory use during parsing, and truncates the result to
    MAX_EXTRACTED_CHARS.
    """
    parts = []
    with pdfplumber.open(file_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            if page_index >= MAX_PDF_PAGES:
                logger.warning(
                    "Stopped PDF text extraction at %d pages (limit %d).",
                    MAX_PDF_PAGES, MAX_PDF_PAGES,
                )
                break
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
    return limit_text_length("\n".join(parts).strip())


def extract_text_with_ocr_fallback(file_path: str) -> str:
    """Extract text with OCR fallback if normal extraction yields little content."""
    text = cached_pdf_text(file_path)

    if len(text) > 100:
        return limit_text_length(text)

    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        return limit_text_length(text)

    try:
        # Prevent memory exhaustion by capping the number of pages converted
        images = convert_from_path(file_path, dpi=150, first_page=1, last_page=MAX_OCR_PAGES, size=1800, timeout=20)
        ocr_parts = []

        for img in images:
            page_text = pytesseract.image_to_string(img, lang=OCR_LANGUAGES, timeout=5)
            if page_text:
                ocr_parts.append(page_text)

        ocr_text = "\n".join(ocr_parts).strip() or text
        logger.info("OCR fallback used for file='%s' extracted=%s chars", file_path, len(ocr_text))
        return limit_text_length(ocr_text)

    except Exception:
        logger.exception("OCR processing failed.")
        return limit_text_length(text)


def is_ocr_available() -> bool:
    """Check if OCR dependencies are available (pytesseract and pdf2image)."""
    try:
        import pytesseract
        import pdf2image
        return True
    except ImportError:
        return False
