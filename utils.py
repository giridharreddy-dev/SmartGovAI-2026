from typing import Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES

def allowed_file(
    file: FileStorage,
) -> Tuple[bool, str]:
    """
    Validate uploaded PDF files.

    Returns:
        (success, message_or_filename)
    """
    if not file:
        return False, "No file uploaded."
    if not file.filename:
        return False, "No file selected."
    filename = secure_filename(file.filename)
    if "." not in filename:
        return False, "Invalid filename."
    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False, "Only PDF files are supported."
    if file.mimetype not in ALLOWED_MIME_TYPES:
        return False, "Invalid file type."
    return True, filename

def voice_text(telugu_data: Dict[str, str], scheme_name: str) -> str:
    """Build a Telugu voice string from the simplified data."""
    return (
        f"{scheme_name}. "
        f"అర్హత: {telugu_data['eligibility']}. "
        f"ప్రయోజనాలు: {telugu_data['benefits']}. "
        f"పత్రాలు: {telugu_data['documents']}. "
        f"దశలు: {telugu_data['steps']}."
    )