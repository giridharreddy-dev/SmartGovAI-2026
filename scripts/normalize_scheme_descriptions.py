#!/usr/bin/env python3
"""Normalize bilingual scheme descriptions in every catalog JSON file.

The catalog has outgrown the original hand-maintained 36-scheme enrichment
list. This pass preserves existing descriptions and fills only missing fields
from the scheme's existing localized sections.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXCLUDED = {"facilities.json", "scheme_schema.json"}

# PMBJP was the first record found without either resolved description.
# Keep this explicit translation rather than manufacturing Telugu from English.
KNOWN_DESCRIPTIONS = {
    "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)": {
        "telugu_description": (
            "ప్రధాన మంత్రి భారతీయ జనౌషధి పరియోజన (PMBJP) ద్వారా జనౌషధి కేంద్రాలలో "
            "నాణ్యమైన జనరిక్ మందులు, శస్త్రచికిత్స సామగ్రి మరియు ఆరోగ్య ఉత్పత్తులు "
            "తక్కువ ధరలకు అందుబాటులో ఉంటాయి. ఈ పథకం ప్రజలకు సరసమైన మందులు పొందడంలో "
            "సహాయపడుతుంది మరియు ఔషధ ఖర్చులను తగ్గిస్తుంది."
        ),
        "english_description": (
            "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP) operates "
            "dedicated Jan Aushadhi Kendras that provide quality generic medicines, "
            "surgical consumables, and health products at affordable prices, helping "
            "citizens reduce the cost of treatment."
        ),
    },
}


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def normalize(name, scheme):
    telugu = scheme.setdefault("telugu", {})
    simplified = scheme.setdefault("simplified", {})

    known = KNOWN_DESCRIPTIONS.get(name, {})
    telugu_description = (
        _text(scheme.get("telugu_description"))
        or _text(telugu.get("description"))
        or _text(known.get("telugu_description"))
    )
    english_description = (
        _text(scheme.get("english_description"))
        or _text(simplified.get("description"))
        or _text(known.get("english_description"))
    )

    # For future scraper records, derive English from the source description.
    if not english_description:
        english_description = _text(scheme.get("original_complex_text"))

    # For records that already have Telugu content but lack the aggregate field,
    # combine the existing localized sections without overwriting valid content.
    if not telugu_description:
        parts = [
            _text(telugu.get("eligibility")),
            _text(telugu.get("benefits")),
            _text(telugu.get("steps")),
        ]
        telugu_description = " ".join(part for part in parts if part)

    if english_description:
        scheme["english_description"] = english_description
        simplified.setdefault("description", english_description)
    if telugu_description:
        scheme["telugu_description"] = telugu_description
        telugu.setdefault("description", telugu_description)


def main():
    changed = []
    incomplete_before = []
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name in EXCLUDED:
            continue
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            continue

        for name, scheme in data.items():
            if not isinstance(scheme, dict):
                continue
            telugu = _text(scheme.get("telugu_description")) or _text(
                scheme.get("telugu", {}).get("description")
            )
            english = _text(scheme.get("english_description")) or _text(
                scheme.get("simplified", {}).get("description")
            )
            if not telugu or not english:
                incomplete_before.append(name)
            before = json.dumps(scheme, ensure_ascii=False, sort_keys=True)
            normalize(name, scheme)
            if before != json.dumps(scheme, ensure_ascii=False, sort_keys=True):
                changed.append(name)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")

    print("Incomplete records before normalization:")
    for name in sorted(set(incomplete_before)):
        print(f"- {name}")
    print(f"Updated {len(set(changed))} scheme records.")


if __name__ == "__main__":
    main()
