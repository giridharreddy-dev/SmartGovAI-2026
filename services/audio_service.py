import os
import uuid

from typing import Dict, Optional

from flask import url_for
from gtts import gTTS

from config import BASE_DIR, AUDIO_DIR
from logger_config import logger

def audio_url_from_static_path(static_path: Optional[str]) -> Optional[str]:
    """Return a Flask URL for an existing audio file, or None if invalid."""
    if not static_path:
        return None
    static_path = static_path.replace("\\", "/")
    abs_path = os.path.join(BASE_DIR, static_path)
    if os.path.exists(abs_path) and os.path.getsize(abs_path) > 0:
        return url_for("static", filename=static_path.removeprefix("static/"))
    return None


def generate_telugu_audio(
    telugu_data: Dict[str, str],
    scheme_name: str,
    static_path: Optional[str] = None,
) -> Optional[str]:
    """Generate Telugu audio for the scheme if not already present."""
    existing_url = audio_url_from_static_path(static_path)
    if existing_url:
        return existing_url
    if static_path:
        filename = os.path.join(BASE_DIR, static_path)
    else:
        filename = os.path.join(AUDIO_DIR, f"{uuid.uuid4()}.mp3")
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        tts = gTTS(text=voice_text(telugu_data, scheme_name), lang="te", slow=False)
        tts.save(filename)
        rel_path = os.path.relpath(filename, os.path.join(BASE_DIR, "static")).replace("\\", "/")
        return url_for("static", filename=rel_path)
    except Exception:
        logger.exception("Audio generation failed for scheme '%s'.", scheme_name)
        return None
    
def voice_text(telugu_data: Dict[str, str], scheme_name: str) -> str:
    """Build a Telugu voice string from the simplified data."""
    return (
        f"{scheme_name}. "
        f"అర్హత: {telugu_data['eligibility']}. "
        f"ప్రయోజనాలు: {telugu_data['benefits']}. "
        f"పత్రాలు: {telugu_data['documents']}. "
        f"దశలు: {telugu_data['steps']}."
    )

