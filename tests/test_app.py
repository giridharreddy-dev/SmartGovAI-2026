import io
import pytest
from unittest.mock import patch

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_404_json_response(client):
    """Test that API clients receiving a 404 get a JSON response."""
    response = client.get("/nonexistent-endpoint", headers={"Accept": "application/json"})
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error_code"] == "NOT_FOUND"


def test_404_html_response(client):
    """Test that browsers receiving a 404 get an HTML fallback page."""
    response = client.get("/nonexistent-endpoint", headers={"Accept": "text/html"})
    assert response.status_code == 404
    assert not response.is_json
    assert b"<html" in response.data.lower()


def test_simplify_missing_scheme_name(client):
    """Test JSON payload missing required parameters."""
    response = client.post("/simplify", json={})
    assert response.status_code == 400
    assert response.get_json()["error_code"] == "MISSING_SCHEME_NAME"


def test_simplify_invalid_file_extension(client):
    """Test upload endpoint with a disallowed file extension."""
    data = {"document": (io.BytesIO(b"dummy data"), "test.txt")}
    response = client.post("/simplify", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error_code"] == "INVALID_FILE_TYPE"


def test_simplify_magic_bytes_failure(client):
    """Test upload endpoint with a valid extension but invalid file header bytes."""
    # Attempting to upload a text file disguised as a PDF
    data = {"document": (io.BytesIO(b"NOT A PDF HEADER..."), "malicious.pdf")}
    response = client.post("/simplify", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error_code"] == "INVALID_PDF"


@patch("app.database.log_request")
@patch("app.extract_text_with_ocr_fallback")
@patch("app.simplify_document")
@patch("app.generate_telugu_audio")
@patch("werkzeug.datastructures.FileStorage.save")
def test_simplify_valid_pdf_upload(mock_save, mock_audio, mock_simplify, mock_extract, mock_log, client):
    """Test successful PDF upload and processing flow."""
    mock_save.return_value = None
    mock_extract.return_value = "Extracted text content"
    mock_simplify.return_value = {
        "simplified": {"eligibility": "Everyone"},
        "telugu": {"eligibility": "అందరూ"}
    }
    mock_audio.return_value = "/static/audio/test.mp3"
    mock_log.return_value = 123

    # File starts with correct magic bytes
    pdf_content = b"%PDF-1.4\n%EOF"
    data = {"document": (io.BytesIO(pdf_content), "scheme_doc.pdf")}
    
    response = client.post("/simplify", data=data, content_type="multipart/form-data")
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["scheme_name"] == "scheme_doc"
    assert json_data["request_id"] == 123
    assert "simplified" in json_data