from unittest.mock import MagicMock
from unittest.mock import patch

from services.pdf_service import extract_text_from_pdf


@patch("services.pdf_service.pdfplumber.open")
def test_extract_pdf(mock_open):
    page = MagicMock()
    page.extract_text.return_value = "Hello"

    pdf = MagicMock()
    pdf.pages = [page]

    mock_open.return_value.__enter__.return_value = pdf

    text = extract_text_from_pdf("dummy.pdf")

    assert text == "Hello"



from unittest.mock import patch

from services.pdf_service import extract_text_with_ocr_fallback


@patch("services.pdf_service.extract_text_from_pdf")
def test_no_ocr_needed(mock_extract):
    mock_extract.return_value = "A" * 200

    result = extract_text_with_ocr_fallback("dummy.pdf")

    assert len(result) == 200

#OCR unavailable

from unittest.mock import patch

from services.pdf_service import extract_text_with_ocr_fallback


@patch("services.pdf_service.extract_text_from_pdf")
@patch("services.pdf_service.OCR_AVAILABLE", False)
def test_ocr_not_available(mock_extract):
    mock_extract.return_value = "short text"

    result = extract_text_with_ocr_fallback("dummy.pdf")

    assert result == "short text"

from unittest.mock import MagicMock
from unittest.mock import patch

from services.pdf_service import extract_text_with_ocr_fallback

#test_OCR_succeeds

from unittest.mock import MagicMock, patch

from services.pdf_service import extract_text_with_ocr_fallback


@patch("services.pdf_service.pytesseract.image_to_string")
@patch("services.pdf_service.convert_from_path")
@patch("services.pdf_service.extract_text_from_pdf")
def test_ocr_success(mock_extract, mock_convert, mock_ocr):
    mock_extract.return_value = "short"

    mock_convert.return_value = [MagicMock(), MagicMock()]
    mock_ocr.side_effect = ["hello", "world"]

    result = extract_text_with_ocr_fallback("dummy.pdf")

    assert result == "hello\nworld"


#test_ocr_failure_returns_original

from unittest.mock import patch

from services.pdf_service import extract_text_with_ocr_fallback


@patch("services.pdf_service.convert_from_path")
@patch("services.pdf_service.extract_text_from_pdf")
def test_ocr_failure_returns_original(mock_extract, mock_convert):
    mock_extract.return_value = "original"

    mock_convert.side_effect = RuntimeError("OCR failed")

    result = extract_text_with_ocr_fallback("dummy.pdf")

    assert result == "original"