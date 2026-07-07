import io
import pytest
from flask import Flask


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True

    with app.test_request_context():
        yield app
import pytest
from werkzeug.datastructures import FileStorage


@pytest.fixture
def sample_telugu_data():
    return {
        "eligibility": "Eligible citizens",
        "benefits": "Free treatment",
        "documents": "Aadhaar",
        "steps": "Visit hospital",
    }


@pytest.fixture
def pdf_file():
    return FileStorage(
        stream=io.BytesIO(b"dummy"),
        filename="sample.pdf",
        content_type="application/pdf",
    )


@pytest.fixture
def txt_file():
    return FileStorage(
        stream=io.BytesIO(b"dummy"),
        filename="sample.txt",
        content_type="text/plain",
    )