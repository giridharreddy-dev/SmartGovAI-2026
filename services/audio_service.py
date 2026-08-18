"""Utilities for generating and resolving Telugu audio assets for schemes."""

import hashlib
import os
import subprocess
import time
from typing import Dict, Optional

from config import AUDIO_DIR, BASE_DIR
from logger_config import logger


def get_relative_audio_path(static_path: Optional[str]) -> Optional[str]:
    """Return a relative path from the static directory for an existing audio file, or None if invalid."""
    if not static_path:
        return None
    static_path = static_path.replace("\\", "/")
    abs_path = os.path.join(BASE_DIR, static_path)
    if os.path.isfile(abs_path) and os.path.getsize(abs_path) > 0:
        logger.info("Reusing existing audio: static_path='%s'", static_path)
        # static_path is structured as static/audio/file.mp3, so we remove the prefix static/
        return static_path.removeprefix("static/")
    return None


def _audio_filename(telugu_data: Dict[str, str], scheme_name: str, static_path: Optional[str] = None) -> str:
    if static_path:
        return os.path.join(BASE_DIR, static_path)
    voice_text_str = voice_text(telugu_data, scheme_name)
    safe_name = hashlib.sha256(voice_text_str.encode("utf-8")).hexdigest()
    scheme_safe = scheme_name.replace(" ", "_").replace("/", "_")
    return os.path.join(AUDIO_DIR, f"{scheme_safe}-{safe_name}.mp3")


def generate_telugu_audio(
    telugu_data: Dict[str, str],
    scheme_name: str,
    static_path: Optional[str] = None,
) -> Optional[str]:
    """Generate Telugu audio for the scheme if not already present, returning the relative static path."""
    existing_rel = get_relative_audio_path(static_path)
    if existing_rel:
        return existing_rel

    filename = _audio_filename(telugu_data, scheme_name, static_path)
    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        rel_path = os.path.relpath(filename, os.path.join(BASE_DIR, "static")).replace("\\", "/")
        logger.info("Reusing generated audio: filename='%s' scheme='%s'", filename, scheme_name)
        return rel_path

    import threading

    def _generate():
        # Use thread ident to prevent concurrent temp file corruption
        tmp_filename = f"{filename}.{threading.get_ident()}.tmp"
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            text_to_speak = voice_text(telugu_data, scheme_name)
            result = subprocess.run(
                ["edge-tts", "--voice", "te-IN-ShrutiNeural", "--text", text_to_speak, "--write-media", tmp_filename],
                capture_output=True,
                text=True,
                check=True
            )
            os.replace(tmp_filename, filename)
            logger.info("Generated audio: filename='%s' scheme='%s'", filename, scheme_name)
        except subprocess.CalledProcessError as e:
            logger.exception("Audio generation failed for scheme '%s'. Error: %s", scheme_name, e.stderr)
            if os.path.exists(tmp_filename):
                try:
                    os.remove(tmp_filename)
                except OSError:
                    pass

    t = threading.Thread(target=_generate, daemon=True)
    t.start()
    t.join(timeout=3.0)

    if t.is_alive():
        logger.warning("Audio generation for scheme '%s' exceeded timeout, returning None to frontend.", scheme_name)
        return None

    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        rel_path = os.path.relpath(filename, os.path.join(BASE_DIR, "static")).replace("\\", "/")
        return rel_path

    return None


def voice_text(telugu_data: Dict[str, str], scheme_name: str) -> str:
    """Build a Telugu voice string from the simplified data."""
    return (
        f"{scheme_name}. "
        f"అర్హత: {telugu_data['eligibility']}. "
        f"ప్రయోజనాలు: {telugu_data['benefits']}. "
        f"పత్రాలు: {telugu_data['documents']}. "
        f"దశలు: {telugu_data['steps']}.")


def cleanup_old_audio(days: int = 7) -> None:
    """Prune audio files older than the specified number of days to prevent disk space exhaustion."""
    if not os.path.exists(AUDIO_DIR):
        return
    
    cutoff_time = time.time() - (days * 86400)
    deleted_count = 0
    
    try:
        for filename in os.listdir(AUDIO_DIR):
            if not filename.endswith(".mp3"):
                continue
                
            file_path = os.path.join(AUDIO_DIR, filename)
            if os.path.isfile(file_path):
                if os.stat(file_path).st_mtime < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
        
        if deleted_count > 0:
            logger.info("Audio cleanup removed %d old mp3 files.", deleted_count)
    except Exception:
        logger.exception("Failed during audio file cleanup.")