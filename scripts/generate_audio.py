"""Generate audio files for the bundled schemes."""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

from config import AUDIO_DIR, BASE_DIR, SCHEMES_DIR
from services.audio_service import voice_text
from services.studio_catalog import load_studio_schemes
from services.studio_narration import STUDIO_VOICES, studio_audio_asset, studio_narration_text
from utils import generate_slug

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2


def load_schemes():
    """Load all scheme definitions from JSON files in the data directory."""
    merged_schemes = {}
    if not os.path.exists(SCHEMES_DIR):
        print(f"Schemes directory '{SCHEMES_DIR}' does not exist.")
        return merged_schemes
        
    for filename in sorted(os.listdir(SCHEMES_DIR)):
        if filename.endswith(".json") and filename not in {"scheme_schema.json", "facilities.json"}:
            filepath = os.path.join(SCHEMES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"Skipping '{filename}': Expected a JSON dictionary.")
                        continue
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
    voice = STUDIO_VOICES["te"]
    temp_path = audio_path_abs + ".tmp"
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            os.makedirs(os.path.dirname(audio_path_abs), exist_ok=True)
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text_to_speak, "--write-media", temp_path],
                capture_output=True,
                text=True,
                check=True,
                timeout=45,
            )
            if not os.path.getsize(temp_path):
                raise RuntimeError("Speech provider returned an empty recording")
            os.replace(temp_path, audio_path_abs)
            print(f"Generated: {audio_path_rel}")
            return
        except (subprocess.SubprocessError, OSError, RuntimeError) as exc:
            last_err = exc
            wait = RETRY_BACKOFF_SECONDS * attempt
            print(f"Failed {name} attempt {attempt}/{MAX_RETRIES}: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(wait)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    raise RuntimeError(f"Failed to generate audio for '{name}': {last_err}")


def _is_mp3(path):
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    with path.open("rb") as source:
        header = source.read(3)
    return header.startswith(b"ID3") or (len(header) >= 2 and header[0] == 255 and header[1] & 224 == 224)


def _studio_synthesizer(provider):
    if provider == "edge":
        import edge_tts

        async def save(text, language, path):
            speech = edge_tts.Communicate(text, STUDIO_VOICES[language], rate="-8%")
            await asyncio.wait_for(speech.save(str(path)), timeout=45)
        return save

    key = os.getenv("SPEECH_KEY", "").strip()
    region = os.getenv("SPEECH_REGION", "").strip().lower()
    if not key or not re.fullmatch(r"[a-z0-9]+", region):
        raise SystemExit("Set SPEECH_KEY and SPEECH_REGION for an authorized Azure Speech resource.")

    def save_azure(text, language, path):
        locale = f"{language}-IN"
        voice = STUDIO_VOICES[language]
        ssml = (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{locale}">'
            f'<voice name="{voice}"><prosody rate="-8%">{escape(text)}</prosody></voice></speak>'
        )
        request = Request(
            f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
            data=ssml.encode("utf-8"),
            headers={
                "Ocp-Apim-Subscription-Key": key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
                "User-Agent": "SmartGovAI",
            },
        )
        with urlopen(request, timeout=45) as response:
            path.write_bytes(response.read())

    async def save(text, language, path):
        await asyncio.to_thread(save_azure, text, language, path)
    return save


async def generate_studio_recordings(schemes, languages, jobs, provider, overwrite):
    root = Path(BASE_DIR) / "static"
    pending = []
    for name, data in schemes.items():
        slug = data.get("slug") or generate_slug(name)
        for language in languages:
            path = root / studio_audio_asset(slug, language)
            if overwrite or not _is_mp3(path):
                pending.append((name, data, language, path))

    print(f"{len(pending)} recording(s) to generate.", flush=True)
    if not pending:
        return 0
    synthesize = _studio_synthesizer(provider)

    async def render(item):
        name, data, language, path = item
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            text = studio_narration_text(name, data, language)
            for attempt in range(MAX_RETRIES):
                try:
                    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".tmp", delete=False) as temp:
                        temp_path = Path(temp.name)
                    await synthesize(text, language, temp_path)
                    if not _is_mp3(temp_path):
                        raise ValueError("The provider returned invalid MP3 data")
                    temp_path.replace(path)
                    print(f"Generated {path.name}", flush=True)
                    return True
                except Exception as error:
                    status = getattr(error, "status", None) or getattr(error, "code", None)
                    if status in {401, 403} or attempt == MAX_RETRIES - 1:
                        detail = f"HTTP {status}" if status else type(error).__name__
                        print(f"Failed {path.name}: {detail}", flush=True)
                        return False
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
                finally:
                    if temp_path is not None:
                        temp_path.unlink(missing_ok=True)
        except ValueError as error:
            print(error, flush=True)
            return False

    # Check each requested voice before starting the batch.
    for language in languages:
        first = next((item for item in pending if item[2] == language), None)
        if first is not None:
            if not await render(first):
                print(f"Stopped before batching after a failed {language} recording.", flush=True)
                return 1
            pending.remove(first)

    semaphore = asyncio.Semaphore(jobs)

    async def render_with_limit(item):
        async with semaphore:
            return await render(item)

    results = await asyncio.gather(*(render_with_limit(item) for item in pending))
    failures = results.count(False)
    print(f"Finished. Failed: {failures}.", flush=True)
    return int(failures > 0)


def main():
    """Generate audio assets for all schemes and report success or failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--studio", action="store_true", help="Generate language-specific audio for Citizen Studio")
    parser.add_argument("--language", choices=("both", "te", "en"), default="both")
    parser.add_argument("--scheme", action="append", help="Select a Studio scheme by exact name or slug. Repeat to select more.")
    parser.add_argument("--jobs", type=int, choices=range(1, 7), default=3)
    parser.add_argument("--provider", choices=("edge", "azure"), default="edge")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate selected Studio recordings")
    args = parser.parse_args()
    if args.studio:
        schemes = {**load_studio_schemes(BASE_DIR), **load_schemes()}
        if args.scheme:
            selected = set(args.scheme)
            matches = {}
            for name, data in schemes.items():
                slug = data.get("slug") or generate_slug(name)
                if name in selected or slug in selected:
                    matches[name] = data
                    selected.discard(name)
                    selected.discard(slug)
            if selected:
                parser.error("Unknown Studio scheme: " + ", ".join(sorted(selected)))
            schemes = matches
        languages = tuple(STUDIO_VOICES) if args.language == "both" else (args.language,)
        sys.exit(asyncio.run(generate_studio_recordings(schemes, languages, args.jobs, args.provider, args.overwrite)))
    if args.scheme or args.language != "both" or args.provider != "edge" or args.overwrite:
        parser.error("--scheme, --language, --provider and --overwrite require --studio")
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
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
