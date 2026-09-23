#!/usr/bin/env python3
"""Normalize bilingual descriptions across the current scheme catalog.

This is intentionally data-driven: it processes every catalog JSON file rather
than relying on the retired 36-scheme hand-maintained list. Existing non-empty
values always win; missing values are filled from the matching localized
sections or, for known records, an explicit curated description.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXCLUDED = {"facilities.json", "scheme_schema.json"}

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


def text(value):
    return value.strip() if isinstance(value, str) else ""


def normalize(name, scheme):
    if not isinstance(scheme, dict):
        return

    telugu = scheme.setdefault("telugu", {})
    simplified = scheme.setdefault("simplified", {})
    if not isinstance(telugu, dict) or not isinstance(simplified, dict):
        return

    known = KNOWN_DESCRIPTIONS.get(name, {})
    te = text(scheme.get("telugu_description")) or text(telugu.get("description"))
    en = text(scheme.get("english_description")) or text(simplified.get("description"))

    # Benefits are the best existing localized fallback for legacy records.
    if not te:
        te = text(telugu.get("benefits"))
    if not en:
        en = text(simplified.get("benefits"))
    if not en:
        en = text(scheme.get("original_complex_text"))

    # Use curated text only where the current record has no usable description.
    te = te or text(known.get("telugu_description"))
    en = en or text(known.get("english_description"))

    if te:
        scheme["telugu_description"] = te
        telugu["description"] = te
    if en:
        scheme["english_description"] = en
        simplified["description"] = en


def inspect(data):
    incomplete = []
    for name, scheme in data.items():
        if not isinstance(scheme, dict):
            incomplete.append(name)
            continue
        telugu = scheme.get("telugu") if isinstance(scheme.get("telugu"), dict) else {}
        simplified = scheme.get("simplified") if isinstance(scheme.get("simplified"), dict) else {}
        te = text(scheme.get("telugu_description")) or text(telugu.get("description"))
        en = text(scheme.get("english_description")) or text(simplified.get("description"))
        if not te or not en:
            incomplete.append(name)
    return incomplete


def main():
    incomplete_before = []
    updated = set()
    files = sorted(path for path in DATA_DIR.glob("*.json") if path.name not in EXCLUDED)

    for path in files:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            continue

        incomplete_before.extend(inspect(data))
        for name, scheme in data.items():
            before = json.dumps(scheme, ensure_ascii=False, sort_keys=True)
            normalize(name, scheme)
            if before != json.dumps(scheme, ensure_ascii=False, sort_keys=True):
                updated.add(name)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")

    remaining = []
    # Re-read after writing so the generator itself verifies its output.
    for path in files:
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            remaining.extend(inspect(data))

    print(f"Incomplete records before normalization: {len(set(incomplete_before))}")
    for name in sorted(set(incomplete_before)):
        print(f"- {name}")
    print(f"Updated records: {len(updated)}")
    if remaining:
        print("Records still incomplete:")
        for name in sorted(set(remaining)):
            print(f"- {name}")
        raise SystemExit(1)
    print("All scheme records have bilingual descriptions.")


if __name__ == "__main__":
    main()
