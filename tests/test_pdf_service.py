import builtins
import types
from unittest.mock import MagicMock, patch

from services.pdf_service import (
    extract_text_from_pdf,
    extract_text_with_ocr_fallback,
    limit_text_length,
    MAX_OCR_PAGES,
    MAX_PDF_PAGES,
)


@patch("services.pdf_service.pdfplumber.open")
def test_extract_pdf(mock_open):
    page = MagicMock()
    page.extract_text.return_value = "Hello"

    pdf = MagicMock()
    pdf.pages = [page]

    mock_open.return_value.__enter__.return_value = pdf

    text = extract_text_from_pdf("dummy.pdf")

    assert text == "Hello"


@patch("services.pdf_service.pdfplumber.open")
def test_extract_pdf_page_limit_enforced(mock_open, monkeypatch):
    """Beyond MAX_PDF_PAGES pages, extraction stops and no more pages are read."""
    monkeypatch.setattr("services.pdf_service.MAX_PDF_PAGES", 2)

    pages = []
    for _ in range(10):
        page = MagicMock()
        page.extract_text.return_value = f"page-{len(pages) + 1}"
        pages.append(page)

    pdf = MagicMock()
    pdf.pages = pages
    mock_open.return_value.__enter__.return_value = pdf

    text = extract_text_from_pdf("large.pdf")

    assert text == "page-1\npage-2"
    # Only 3 pages were touched (2 appended + 1 checked against the limit)
    assert pages[2].extract_text.call_count == 0, "extraction should stop at the page limit"


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
def test_ocr_page_limit_enforced(mock_cached):
    """Ensure the OCR fallback bounds checks the page count to prevent memory DoS."""
    mock_cached.return_value = "short"

    fake_pytesseract = MagicMock()
    pdf2image_module = types.ModuleType("pdf2image")
    mock_convert = MagicMock(return_value=[])
    pdf2image_module.convert_from_path = mock_convert

    with patch.dict("sys.modules", {"pytesseract": fake_pytesseract, "pdf2image": pdf2image_module}):
        extract_text_with_ocr_fallback("dummy.pdf")

    mock_convert.assert_called_once()
    _, kwargs = mock_convert.call_args
    assert kwargs.get("first_page") == 1
    assert kwargs.get("last_page") == MAX_OCR_PAGES


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


def test_limit_text_length_no_truncation_when_within_limit():
    text = "A" * 10
    assert limit_text_length(text, limit=100) == text


def test_limit_text_length_truncates_over_limit():
    text = "A" * 200
    result = limit_text_length(text, limit=50)
    assert result == "A" * 50
    assert len(result) == 50


def test_limit_text_length_nonpositive_limit_returns_unchanged():
    text = "hello"
    assert limit_text_length(text, limit=0) == text


@patch("services.pdf_service.pdfplumber.open")
def test_extract_pdf_text_length_limit_enforced(mock_open, monkeypatch):
    """Plain extraction truncates the combined text to MAX_EXTRACTED_CHARS (default 50k)."""
    monkeypatch.setattr("services.pdf_service.MAX_PDF_PAGES", 100)

    pages = []
    for _ in range(100):
        page = MagicMock()
        page.extract_text.return_value = "X" * 600  # 100 x 600 chars = 60k > 50k default
        pages.append(page)

    pdf = MagicMock()
    pdf.pages = pages
    mock_open.return_value.__enter__.return_value = pdf

    text = extract_text_from_pdf("long_text.pdf")

    # 60k-char combined text is capped back to the configured limit
    assert len(text) == 50000


@patch("services.pdf_service.cached_pdf_text")
def test_ocr_path_text_length_limit_enforced(mock_cached):
    """OCR fallback output is truncated to MAX_EXTRACTED_CHARS (default 50k)."""
    mock_cached.return_value = "short"

    fake_pytesseract = MagicMock()
    fake_pytesseract.image_to_string.side_effect = ["A" * 30000, "B" * 30000]  # 60k > 50k

    pdf2image_module = types.ModuleType("pdf2image")
    pdf2image_module.convert_from_path = MagicMock(return_value=[MagicMock(), MagicMock()])

    with patch.dict("sys.modules", {"pytesseract": fake_pytesseract, "pdf2image": pdf2image_module}):
        result = extract_text_with_ocr_fallback("dummy.pdf")

    assert len(result) == 50000

@patch("services.pdf_service.pdfplumber.open")
def test_blank_pages_count_toward_page_limit(mock_open, monkeypatch):
    monkeypatch.setattr("services.pdf_service.MAX_PDF_PAGES", 2)
    pages = [MagicMock() for _ in range(4)]
    for page in pages:
        page.extract_text.return_value = ""
    mock_open.return_value.__enter__.return_value.pages = pages
    assert extract_text_from_pdf("blank.pdf") == ""
    assert [page.extract_text.call_count for page in pages] == [1, 1, 0, 0]
