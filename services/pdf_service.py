import pdfplumber

from logger_config import logger

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_with_ocr_fallback(file_path: str) -> str:
    """Extract text with OCR fallback if normal extraction yields little content."""
    text = extract_text_from_pdf(file_path)

    if len(text) > 100:
        return text

    if not OCR_AVAILABLE:
        return text

    try:
        images = convert_from_path(file_path, dpi=200)
        ocr_text = ""

        for img in images:
            ocr_text += pytesseract.image_to_string(img, lang="tel+eng") + "\n"

        return ocr_text.strip()

    except Exception:
        logger.exception("OCR processing failed.")
        return text
    
def is_ocr_available() -> bool:
    return OCR_AVAILABLE