"""Utility script for generating Telugu audio files for the bundled schemes."""

import json
import os
import time

from config import AUDIO_DIR, BASE_DIR, SCHEMES_DIR, VOICE_LANGUAGE
from gtts import gTTS
from gtts.tts import gTTSError
from services.audio_service import voice_text

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2


def load_schemes():
    """Load all scheme definitions from JSON files in the data directory."""
    merged_schemes = {}
    if not os.path.exists(SCHEMES_DIR):
        print(f"Schemes directory '{SCHEMES_DIR}' does not exist.")
        return merged_schemes
        
    for filename in sorted(os.listdir(SCHEMES_DIR)):
        if filename.endswith(".json") and filename != "scheme_schema.json":
            filepath = os.path.join(SCHEMES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for scheme_name, scheme_data in data.items():
                        if "telugu" in scheme_data:
                            merged_schemes[scheme_name] = scheme_data
            except Exception as e:
                print(f"Failed to load or parse scheme file '{filename}': {e}")
    return merged_schemes


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

    text_to_speak = voice_text(data["telugu"], name)
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            os.makedirs(os.path.dirname(audio_path_abs), exist_ok=True)
            gTTS(text=text_to_speak, lang=VOICE_LANGUAGE, slow=False).save(audio_path_abs)
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
