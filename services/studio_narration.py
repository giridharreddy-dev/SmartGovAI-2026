"""Names and scripts for Citizen Studio's generated scheme recordings."""

from pathlib import Path

STUDIO_VOICES = {"te": "te-IN-ShrutiNeural", "en": "en-IN-NeerjaNeural"}
_RECORDINGS = Path("audio") / "studio" / "bilingual"


def studio_audio_asset(slug, language):
    return _RECORDINGS / f"{slug}.{language}.mp3"


def studio_narration_text(name, scheme, language):
    if language == "te":
        title = scheme.get("telugu_name") or "పథకం వివరాలు"
        sections = scheme["telugu"]
    else:
        title = name
        sections = scheme["simplified"]

    summary = sections.get("description") or sections.get("benefits")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError(f"Missing {language} summary for {name}")
    summary = " ".join(summary.split())
    title = " ".join(title.split()).rstrip(".!?")
    return f"{title}. {summary}"
