from unittest.mock import MagicMock
from unittest.mock import patch

from services.gemini_service import simplify_document


@patch("services.gemini_service.client")
def test_valid_json(mock_client):
    response = MagicMock()

    response.text = """
{
"simplified":{},
"telugu":{}
}
"""

    mock_client.models.generate_content.return_value = response

    result = simplify_document("abc", "scheme")

    assert "simplified" in result
    assert "telugu" in result

import pytest
from unittest.mock import MagicMock
from unittest.mock import patch

from services.gemini_service import simplify_document


@patch("services.gemini_service.client")
def test_invalid_json(mock_client):

    response = MagicMock()
    response.text = "Not JSON"

    mock_client.models.generate_content.return_value = response

    with pytest.raises(ValueError):
        simplify_document("abc", "scheme")

#Missing simplified key

import pytest
from unittest.mock import MagicMock
from unittest.mock import patch

from services.gemini_service import simplify_document


@patch("services.gemini_service.client")
def test_missing_simplified(mock_client):
    response = MagicMock()

    response.text = """
{
    "telugu": {}
}
"""

    mock_client.models.generate_content.return_value = response

    with pytest.raises(ValueError):
        simplify_document("abc", "scheme")

#Missing telugu key

@patch("services.gemini_service.client")
def test_missing_telugu(mock_client):
    response = MagicMock()

    response.text = """
{
    "simplified": {}
}
"""

    mock_client.models.generate_content.return_value = response

    with pytest.raises(ValueError):
        simplify_document("abc", "scheme")

#Gemini not available
@patch("services.gemini_service.client", None)
def test_client_not_available():

    with pytest.raises(RuntimeError):
        simplify_document("abc", "scheme")