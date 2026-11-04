"""Rebuild the Citizen Studio master catalog and report unlinked V2 records."""

import argparse
import json
import os
import tempfile
import unicodedata
from collections import defaultdict
from pathlib import Path

from services.studio_catalog import CATALOG_PATH, load_directory_source


def normalized_title(value):
    return "".join(char for char in unicodedata.normalize("NFKC", value).casefold() if char.isalnum())


def fill_missing(existing, incoming):
    """Fill missing values recursively while retaining the preferred source."""
    if isinstance(existing, dict) and isinstance(incoming, dict):
        return {**existing, **{key: fill_missing(existing.get(key), value) for key, value in incoming.items()}}
    if existing is None or existing == [] or existing == {} or (
        isinstance(existing, str) and not existing.strip()
    ):
        return incoming
    return existing


def reconcile_catalog(existing, directory, v2):
    catalog = {
        name: fill_missing(record, directory.get(name, {})) for name, record in existing.items()
    }
    for name, record in directory.items():
        if name not in existing:
            catalog[name] = record
        elif not existing[name].get("directory_entry"):
            catalog[name].pop("directory_entry", None)
            # Preserve the legacy ID and the surface it is already available on.
            if "slug" not in existing[name]:
                catalog[name].pop("slug", None)
    titles = defaultdict(list)
    for name in catalog:
        titles[normalized_title(name)].append(name)

    v2_title_counts = defaultdict(int)
    for name in v2:
        v2_title_counts[normalized_title(name)] += 1
    report = {"matched": [], "pending_review": []}
    for title, record in v2.items():
        key = normalized_title(title)
        matches = titles.get(key, [])
        ambiguous = len(matches) > 1 or v2_title_counts[key] > 1
        matched = catalog[matches[0]] if len(matches) == 1 and not ambiguous else None
        same_region = matched is not None and (
            normalized_title(matched.get("level") or "") == normalized_title(record.get("level") or "")
        )
        if not same_region:
            reason = "ambiguous_title" if ambiguous else "region_mismatch" if matches else "unlinked_title"
            report["pending_review"].append({
                "title": title, "reason": reason, "candidate_titles": matches, "v2_record": record,
            })
            continue
        name = matches[0]
        current = matched.get("required_documents") or []
        documents = record.get("required_documents") or []
        action = "retained"
        if documents and not current and not (matched.get("operations") or {}).get("required_documents"):
            catalog[name] = fill_missing(matched, {"required_documents": documents})
            action = "filled"
        elif documents and documents != current:
            action = "review_checklist_difference"
        report["matched"].append({
            "v2_title": title, "catalog_title": name, "document_action": action,
            "catalog_documents_before": current, "v2_documents": documents,
            "v2_source_url": record.get("official_website") or record.get("source_url"),
        })
    report["summary"] = {
        "catalog_records": len(catalog),
        "v2_records": len(v2),
        "v2_records_with_documents": sum(bool(row.get("required_documents")) for row in v2.values()),
        "matched": len(report["matched"]),
        "pending_review": len(report["pending_review"]),
        "checklists_filled": sum(row["document_action"] == "filled" for row in report["matched"]),
        "checklist_differences": sum(row["document_action"] == "review_checklist_difference" for row in report["matched"]),
    }
    return catalog, report


def read_records(path):
    records = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(records, dict) or not records or any(not isinstance(row, dict) for row in records.values()):
        raise ValueError(f"Expected an object of named scheme records in {path}")
    return records


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            json.dump(value, output, ensure_ascii=False, indent=2)
            output.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("v2_master", type=Path)
    parser.add_argument("--catalog", type=Path, default=root / CATALOG_PATH)
    parser.add_argument("--directory", type=Path, default=root / "data/studio/welfare.json")
    parser.add_argument("--output", required=True, type=Path, help="Write the unified catalog to this path")
    parser.add_argument("--review-output", required=True, type=Path, help="Write unmatched titles and checklist comparisons")
    args = parser.parse_args()
    if args.review_output.resolve() in {path.resolve() for path in (args.catalog, args.v2_master, args.directory, args.output)}:
        parser.error("The review output needs its own path")
    if args.output.resolve() in {args.v2_master.resolve(), args.directory.resolve()}:
        parser.error("The catalog output cannot overwrite the V2 or directory source")
    catalog, report = reconcile_catalog(
        read_records(args.catalog), load_directory_source(args.directory), read_records(args.v2_master)
    )
    write_json(args.review_output, report)
    write_json(args.output, catalog)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
