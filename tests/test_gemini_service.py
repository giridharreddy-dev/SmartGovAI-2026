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