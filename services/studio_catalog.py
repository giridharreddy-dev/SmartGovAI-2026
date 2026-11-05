"""Load the separately sourced, cross-sector Citizen Studio directory."""

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from services.scheme_operations import SchemeOperations

from utils import generate_slug

CATALOG_PATH = Path("data/merged_schemes.json")


def load_master_catalog(root):
    path = Path(root) / CATALOG_PATH
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict) or not catalog or any(
        not name or not isinstance(row, dict) for name, row in catalog.items()
    ):
        raise ValueError(f"Invalid master scheme catalog: {path}")
    from services.canonical_catalog import runtime_record
    catalog = {name: runtime_record(row) for name, row in catalog.items()}
    for name, row in catalog.items():
        row.setdefault("slug", generate_slug(name))
    return catalog


def load_legacy_catalog(root):
    return {name: row for name, row in load_master_catalog(root).items() if not row.get("directory_entry")}


SECTORS = frozenset({
    "agriculture", "finance", "business", "education", "health", "housing", "law",
    "science", "employment", "welfare", "sports", "transport", "tourism", "utility", "women",
})


def load_directory_source(path):
    """Convert the offline directory source into canonical catalog records."""
    path = Path(path)

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
            "required_documents": [],
        }
        if "operations" in row:
            try:
                reviewed = date.fromisoformat(row.get("operationsReviewed", "")).isoformat()
            except (TypeError, ValueError) as error:
                raise ValueError(f"Operational details for {name} need a source review date") from error
            schemes[name]["operations"] = SchemeOperations.model_validate(row["operations"]).model_dump(mode="json")
            schemes[name]["operations_reviewed"] = reviewed
    return schemes
