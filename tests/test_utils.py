
from utils import allowed_file


def test_valid_pdf(pdf_file):
    ok, filename = allowed_file(pdf_file)

    assert ok is True
    assert filename == "sample.pdf"


def test_invalid_extension(txt_file):
    ok, msg = allowed_file(txt_file)

    assert ok is False
    assert msg == "Only PDF files are supported."

#No file uploaded
def test_none_file():
    ok, msg = allowed_file(None)

    assert ok is False
    assert msg == "No file uploaded."

#No filename

import io
from werkzeug.datastructures import FileStorage

from utils import allowed_file


def test_empty_filename():
    file = FileStorage(
        stream=io.BytesIO(b""),
        filename="",
        content_type="application/pdf",
    )

    ok, _ = allowed_file(file)

    assert ok is False

#Invalid MIMEname

def test_invalid_mimetype():
    file = FileStorage(
        stream=io.BytesIO(b""),
        filename="test.pdf",
        content_type="text/plain",
    )

    ok, _ = allowed_file(file)

    assert ok is False

#No extension

def test_no_extension():
    file = FileStorage(
        stream=io.BytesIO(b""),
        filename="document",
        content_type="application/pdf",
    )

    ok, _ = allowed_file(file)

    assert ok is False