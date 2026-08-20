import io
import pytest
from unittest.mock import patch
from werkzeug.exceptions import TooManyRequests

from app import app, handle_unexpected_exception


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


def test_http_exception_status_is_preserved(app):
    """Framework errors, such as rate limiting, must not become HTTP 500."""
    error = TooManyRequests()
    with app.test_request_context("/some-html-endpoint", headers={"Accept": "text/html"}):
        from app import handle_unexpected_exception
        assert handle_unexpected_exception(error) is error


def test_offline_cache_uses_static_relative_audio_urls(client):
    response = client.get("/offline-cache")

    assert response.status_code == 200
    voice_urls = [
        scheme["voice_url"]
        for scheme in response.get_json()["schemes_list"].values()
        if scheme["voice_url"]
    ]
    assert voice_urls
    assert all("/static/static/" not in url for url in voice_urls)


def test_facilities_reject_negative_radius(client):
    response = client.get("/api/facilities?lat=15.0&lng=78.0&radius=-1")

    assert response.status_code == 400
    assert response.get_json()["error_code"] == "INVALID_RADIUS"


@patch("app.generate_chat_response", return_value=None)
def test_chat_uses_catalog_fallback_without_gemini(_mock_chat, client):
    response = client.post("/chat", json={"question": "ఉచిత చికిత్స కావాలి"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["used_ai"] is False
    assert payload["matched_schemes"]
    assert "అధికారిక కార్యాలయం" in payload["answer"]


def test_chat_rejects_missing_question(client):
    response = client.post("/chat", json={})

    assert response.status_code == 400
    assert response.get_json()["error_code"] == "MISSING_QUESTION"


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
    data = {
        "document": (io.BytesIO(b"NOT A PDF HEADER..."), "malicious.pdf"),
        "consent": "true"
    }
    response = client.post("/simplify", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error_code"] == "INVALID_PDF"


@patch("app.is_gemini_available", return_value=True)
@patch("app.validate_pdf_content", return_value=(True, ""))
@patch("app.database.log_request")
@patch("app.extract_text_with_ocr_fallback")
@patch("app.simplify_document")
@patch("app.generate_telugu_audio")
@patch("werkzeug.datastructures.FileStorage.save")
def test_simplify_valid_pdf_upload(mock_save, mock_audio, mock_simplify, mock_extract, mock_log, mock_validate, mock_gemini, client):
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
    data = {
        "document": (io.BytesIO(pdf_content), "scheme_doc.pdf"),
        "consent": "true",
    }
    
    response = client.post("/simplify", data=data, content_type="multipart/form-data")
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["scheme_name"] == "scheme_doc"
    assert json_data["request_id"] is None
    assert "simplified" in json_data


def test_analytics_requires_admin_token(client):
    """Test that /analytics returns 401 without a valid admin token."""
    response = client.get("/analytics")
    assert response.status_code == 401


def test_analytics_with_valid_token(client, monkeypatch):
    """Test that /analytics returns 200 with a valid admin token."""
    monkeypatch.setenv("ADMIN_TOKEN", "test-token")
    response = client.get("/analytics", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200




def test_healthz_endpoint(client):
    """Test /healthz returns status and diagnostic information."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "schemes" not in data


def test_health_alias(client):
    """Test /health alias for /healthz."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_readyz_endpoint(client):
    """Test /readyz returns status and deeper diagnostic information."""
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "schemes" in data


def test_healthz_rate_limit_exemption(client):
    """Test that /healthz is not rate limited."""
    from app import app
    app.config["RATELIMIT_ENABLED"] = True
    try:
        # Default limit is 50 per hour. 55 requests would trigger 429 if not exempt.
        for _ in range(55):
            res = client.get("/healthz")
            assert res.status_code == 200
    finally:
        app.config["RATELIMIT_ENABLED"] = False


def test_version_endpoint(client):
    """Test /version endpoint returns API metadata."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == "1.0.0"
    assert "startup_time" in data


def test_scheme_by_valid_and_invalid_slug(client):
    """Test slug routing with both existing and nonexistent slugs."""
    # Nonexistent slug should redirect to index
    res_404 = client.get("/scheme/nonexistent-invalid-slug")
    assert res_404.status_code in (302, 200)

    # Valid slug test if schemes exist
    from app import slug_to_scheme
    if slug_to_scheme:
        sample_slug = next(iter(slug_to_scheme.keys()))
        res_valid = client.get(f"/scheme/{sample_slug}")
        assert res_valid.status_code == 200


def test_qr_code_generation(client):
    """Test /qr/<slug>.png returns valid PNG image data."""
    from app import slug_to_scheme
    if slug_to_scheme:
        sample_slug = next(iter(slug_to_scheme.keys()))
        res = client.get(f"/qr/{sample_slug}.png")
        assert res.status_code == 200
        assert res.mimetype == "image/png"
        assert res.data.startswith(b"\x89PNG")

    # Invalid slug should 404
    res_invalid = client.get("/qr/invalid-slug-12345.png")
    assert res_invalid.status_code == 404

from google.genai import errors as genai_errors

@patch("app.is_gemini_available", return_value=True)
@patch("werkzeug.datastructures.FileStorage.save", return_value=None)
@patch("app.validate_pdf_content", return_value=(True, ""))
@patch("app.extract_text_with_ocr_fallback", return_value="text")
@patch("app.simplify_document")
def test_simplify_pdf_gemini_server_error_returns_json_503(mock_simplify, mock_extract, mock_validate, mock_save, mock_gemini, client):
    mock_simplify.side_effect = genai_errors.ServerError(code=503, response_json={}, response=None)
    data = {"scheme_name": "test"}
    file = (io.BytesIO(b"%PDF-1.4\nTest"), "test.pdf")
    res = client.post("/simplify", data={"document": file, "scheme_name": "test", "consent": "true"}, content_type="multipart/form-data")
    assert res.status_code == 503
    assert res.is_json
    assert res.get_json()["error_code"] == "AI_SERVICE_UNAVAILABLE"

@patch("app.is_gemini_available", return_value=True)
@patch("werkzeug.datastructures.FileStorage.save", return_value=None)
@patch("app.validate_pdf_content", return_value=(True, ""))
@patch("app.extract_text_with_ocr_fallback", return_value="text")
@patch("app.simplify_document")
def test_simplify_pdf_gemini_client_error_429_returns_json_503(mock_simplify, mock_extract, mock_validate, mock_save, mock_gemini, client):
    mock_simplify.side_effect = genai_errors.ClientError(code=429, response_json={}, response=None)
    file = (io.BytesIO(b"%PDF-1.4\nTest"), "test.pdf")
    res = client.post("/simplify", data={"document": file, "scheme_name": "test", "consent": "true"}, content_type="multipart/form-data")
    assert res.status_code == 503
    assert res.is_json
    assert res.get_json()["error_code"] == "AI_RATE_LIMITED"

@patch("app.is_gemini_available", return_value=True)
@patch("werkzeug.datastructures.FileStorage.save", return_value=None)
@patch("app.validate_pdf_content", return_value=(True, ""))
@patch("app.extract_text_with_ocr_fallback", return_value="text")
@patch("app.simplify_document")
def test_simplify_pdf_gemini_client_error_401_returns_json_502(mock_simplify, mock_extract, mock_validate, mock_save, mock_gemini, client):
    mock_simplify.side_effect = genai_errors.ClientError(code=401, response_json={}, response=None)
    file = (io.BytesIO(b"%PDF-1.4\nTest"), "test.pdf")
    res = client.post("/simplify", data={"document": file, "scheme_name": "test", "consent": "true"}, content_type="multipart/form-data")
    assert res.status_code == 502
    assert res.is_json
    assert res.get_json()["error_code"] == "AI_CONFIGURATION_ERROR"

@patch("app.is_gemini_available", return_value=True)
@patch("werkzeug.datastructures.FileStorage.save", return_value=None)
@patch("app.validate_pdf_content", return_value=(True, ""))
@patch("app.extract_text_with_ocr_fallback", return_value="text")
@patch("app.simplify_document")
def test_simplify_pdf_gemini_client_error_400_returns_json_502(mock_simplify, mock_extract, mock_validate, mock_save, mock_gemini, client):
    mock_simplify.side_effect = genai_errors.ClientError(code=400, response_json={}, response=None)
    file = (io.BytesIO(b"%PDF-1.4\nTest"), "test.pdf")
    res = client.post("/simplify", data={"document": file, "scheme_name": "test", "consent": "true"}, content_type="multipart/form-data")
    assert res.status_code == 502
    assert res.is_json
    assert res.get_json()["error_code"] == "AI_SIMPLIFICATION_FAILED"

@patch("app.is_gemini_available", return_value=True)
@patch("werkzeug.datastructures.FileStorage.save", return_value=None)
@patch("app.validate_pdf_content", return_value=(True, ""))
@patch("app.extract_text_with_ocr_fallback", return_value="text")
@patch("app.simplify_document")
def test_simplify_pdf_unexpected_error_returns_json_500(mock_simplify, mock_extract, mock_validate, mock_save, mock_gemini, client):
    mock_simplify.side_effect = TypeError("Unexpected")
    file = (io.BytesIO(b"%PDF-1.4\nTest"), "test.pdf")
    res = client.post("/simplify", data={"document": file, "scheme_name": "test", "consent": "true"}, content_type="multipart/form-data")
    assert res.status_code == 500
    assert res.is_json
    assert res.get_json()["error_code"] == "INTERNAL_SERVER_ERROR"
