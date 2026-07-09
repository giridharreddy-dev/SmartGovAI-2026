import builtins
import types
from unittest.mock import MagicMock, patch

from services.pdf_service import extract_text_from_pdf, extract_text_with_ocr_fallback


@patch("services.pdf_service.pdfplumber.open")
def test_extract_pdf(mock_open):
    page = MagicMock()
    page.extract_text.return_value = "Hello"

    pdf = MagicMock()
    pdf.pages = [page]

    mock_open.return_value.__enter__.return_value = pdf

    text = extract_text_from_pdf("dummy.pdf")

    assert text == "Hello"


@patch("services.pdf_service.cached_pdf_text")
def test_no_ocr_needed(mock_cached):
    mock_cached.return_value = "A" * 200

    result = extract_text_with_ocr_fallback("dummy.pdf")

    assert len(result) == 200


@patch("services.pdf_service.cached_pdf_text")
def test_ocr_not_available(mock_cached):
    mock_cached.return_value = "short text"
    real_import = builtins.__import__

    def failing_import(name, *args, **kwargs):
        if name in {"pytesseract", "pdf2image"}:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=failing_import):
        result = extract_text_with_ocr_fallback("dummy.pdf")

    assert result == "short text"


@patch("services.pdf_service.cached_pdf_text")
def test_ocr_success(mock_cached):
    mock_cached.return_value = "short"

    fake_pytesseract = MagicMock()
    fake_pytesseract.image_to_string.side_effect = ["hello", "world"]

    pdf2image_module = types.ModuleType("pdf2image")
    pdf2image_module.convert_from_path = MagicMock(return_value=[MagicMock(), MagicMock()])

    with patch.dict("sys.modules", {"pytesseract": fake_pytesseract, "pdf2image": pdf2image_module}):
        result = extract_text_with_ocr_fallback("dummy.pdf")

    assert result == "hello\nworld"


@patch("services.pdf_service.cached_pdf_text")
def test_ocr_failure_returns_original(mock_cached):
    mock_cached.return_value = "original"

    fake_pytesseract = MagicMock()
    fake_pytesseract.image_to_string.side_effect = RuntimeError("OCR failed")

    pdf2image_module = types.ModuleType("pdf2image")
    pdf2image_module.convert_from_path = MagicMock(side_effect=RuntimeError("OCR failed"))

    with patch.dict("sys.modules", {"pytesseract": fake_pytesseract, "pdf2image": pdf2image_module}):
        result = extract_text_with_ocr_fallback("dummy.pdf")

    assert result == "original"