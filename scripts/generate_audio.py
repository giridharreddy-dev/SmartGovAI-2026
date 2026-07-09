"""Utility script for generating Telugu audio files for the bundled schemes."""

import json
import os
import time

from config import AUDIO_DIR, BASE_DIR, SCHEMES_PATH, VOICE_LANGUAGE
from gtts import gTTS
from gtts.tts import gTTSError

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2


def load_schemes():
    """Load the scheme definitions from the JSON file used by the app."""
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_voice_text(name, data):
    """Construct the spoken Telugu text for a scheme from its structured data."""
    telugu = data["telugu"]
    display_name = data.get("telugu_name") or name
    return (
        f"{display_name}. "
        f"అర్హత: {telugu['eligibility']}. "
        f"ప్రయోజనాలు: {telugu['benefits']}. "
        f"పత్రాలు: {telugu['documents']}. "
        f"దశలు: {telugu['steps']}."
    )


def generate_audio_for_scheme(name, data):
    """Generate and save an MP3 audio file for a single scheme when needed."""
    audio_path_rel = data.get("audio_file")
    if not audio_path_rel:
        print(f"Skipping without audio_file: {name}")
        return

    audio_path_abs = os.path.join(BASE_DIR, audio_path_rel)
    if os.path.exists(audio_path_abs) and os.path.getsize(audio_path_abs) > 0:
        print(f"Skipping existing: {audio_path_rel}")
        return

    voice_text = build_voice_text(name, data)
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            os.makedirs(os.path.dirname(audio_path_abs), exist_ok=True)
            gTTS(text=voice_text, lang=VOICE_LANGUAGE, slow=False).save(audio_path_abs)
            print(f"Generated: {audio_path_rel}")
            return
        except (gTTSError, Exception) as exc:
            last_err = exc
            wait = RETRY_BACKOFF_SECONDS * attempt
            print(f"Failed {name} attempt {attempt}/{MAX_RETRIES}: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(wait)

    raise RuntimeError(f"Failed to generate audio for '{name}': {last_err}")


def main():
    """Generate audio assets for all schemes and report success or failure."""
    schemes = load_schemes()
    os.makedirs(AUDIO_DIR, exist_ok=True)

    ok = 0
    failed = 0
    for name, data in schemes.items():
        try:
            generate_audio_for_scheme(name, data)
            ok += 1
        except Exception as exc:
            failed += 1
            print(f"Giving up on {name}: {exc}")

    print(f"Done. Success: {ok}, Failed: {failed}")


if __name__ == "__main__":
    main()
