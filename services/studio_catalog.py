"""Load the separately sourced, cross-sector Citizen Studio directory."""

import json
from pathlib import Path
from urllib.parse import urlsplit

SECTORS = frozenset({
    "agriculture", "finance", "business", "education", "health", "housing", "law",
    "science", "employment", "welfare", "sports", "transport", "tourism", "utility", "women",
})


def load_studio_schemes(root):
    path = Path(root) / "data" / "studio" / "welfare.json"
    if not path.is_file():
        return {}

    catalog = json.loads(path.read_text(encoding="utf-8"))
    schemes = {}
    ids = set()
    for row in catalog["schemes"]:
        name = row["name"]
        slug = "welfare-" + row["id"]
        source = urlsplit(row["url"])
        if (name in schemes or slug in ids or row["sector"] not in SECTORS
                or source.scheme != "https" or not source.hostname
                or source.username or source.password):
            raise ValueError(f"Invalid or duplicate Citizen Studio entry: {name}")
        ids.add(slug)
        schemes[name] = {
            "slug": slug,
            "level": row.get("region", "National"),
            "category": row["category"],
            "sector": row["sector"],
            "telugu_name": row.get("nameTe", ""),
            "keywords": row["keywords"],
            "simplified": {"description": row["summary"]},
            "telugu": {"description": row["summaryTe"]},
            "source_name": row["publisher"],
            "official_website": row["url"],
            "source_reviewed": catalog["reviewed"],
            "directory_entry": True,
        }
    return schemes
