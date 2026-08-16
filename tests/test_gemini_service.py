import pytest
from unittest.mock import MagicMock, patch

from services.gemini_service import simplify_document


@patch("services.gemini_service.get_client")
def test_valid_json(mock_get_client):
    response = MagicMock()
    response.text = """
{
"simplified":{},
"telugu":{}
}
"""

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = response
    mock_get_client.return_value = mock_client

    result = simplify_document("abc", "scheme")

    assert "simplified" in result
    assert "telugu" in result


@patch("services.gemini_service.get_client")
def test_invalid_json(mock_get_client):
    response = MagicMock()
    response.text = "Not JSON"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = response
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError):
        simplify_document("abc", "scheme")


@patch("services.gemini_service.get_client")
def test_missing_simplified(mock_get_client):
    response = MagicMock()
    response.text = """
{
    "telugu": {}
}
"""

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = response
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError):
        simplify_document("abc", "scheme")


@patch("services.gemini_service.get_client")
def test_missing_telugu(mock_get_client):
    response = MagicMock()
    response.text = """
{
    "simplified": {}
}
"""

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = response
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError):
        simplify_document("abc", "scheme")


@patch("services.gemini_service.get_client")
def test_client_not_available(mock_get_client):
    mock_get_client.return_value = None

    with pytest.raises(RuntimeError):
        simplify_document("abc", "scheme")

import services.gemini_service as gemini_service
from google.genai import errors as genai_errors

@patch("services.gemini_service._call_gemini")
@patch("services.gemini_service.get_client")
@patch("services.gemini_service.time.sleep")
def test_server_error_retry_then_success(mock_sleep, mock_get_client, mock_call):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Needs 1 retry
    mock_call.side_effect = [
        genai_errors.ServerError(code=503, response_json={}, response=None),
        {"simplified": {}, "telugu": {}}
    ]

    result = simplify_document("abc", "scheme")
    assert "simplified" in result
    assert mock_call.call_count == 2
    assert mock_sleep.call_count == 1

@patch("services.gemini_service._call_gemini")
@patch("services.gemini_service.get_client")
@patch("services.gemini_service.time.sleep")
def test_server_error_all_retries_exhausted(mock_sleep, mock_get_client, mock_call):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_call.side_effect = genai_errors.ServerError(code=503, response_json={}, response=None)

    with pytest.raises(genai_errors.ServerError):
        simplify_document("abc", "scheme")
    
    assert mock_call.call_count == gemini_service.GEMINI_MAX_RETRIES

@patch("services.gemini_service._call_gemini")
@patch("services.gemini_service.get_client")
@patch("services.gemini_service.time.sleep")
def test_client_error_not_retried(mock_sleep, mock_get_client, mock_call):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_call.side_effect = genai_errors.ClientError(code=400, response_json={}, response=None)

    with pytest.raises(genai_errors.ClientError):
        simplify_document("abc", "scheme")
    
    assert mock_call.call_count == 1
    assert mock_sleep.call_count == 0

@patch("services.gemini_service._call_gemini")
@patch("services.gemini_service.get_client")
@patch("services.gemini_service.time.sleep")
def test_rate_limit_429_is_retried(mock_sleep, mock_get_client, mock_call):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Needs 1 retry
    mock_call.side_effect = [
        genai_errors.ClientError(code=429, response_json={}, response=None),
        {"simplified": {}, "telugu": {}}
    ]

    result = simplify_document("abc", "scheme")
    assert "simplified" in result
    assert mock_call.call_count == 2
    assert mock_sleep.call_count == 1

def test_is_retryable_classification():
    from services.gemini_service import _is_retryable_gemini_error
    
    err_503 = genai_errors.ServerError(code=503, response_json={}, response=None)
    assert _is_retryable_gemini_error(err_503) is True
    
    err_429 = genai_errors.ClientError(code=429, response_json={}, response=None)
    assert _is_retryable_gemini_error(err_429) is True
    
    err_400 = genai_errors.ClientError(code=400, response_json={}, response=None)
    assert _is_retryable_gemini_error(err_400) is False
    
    err_other = ValueError("json")
    assert _is_retryable_gemini_error(err_other) is False