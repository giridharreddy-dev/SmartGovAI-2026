"""Rebuild the Citizen Studio master catalog and report unlinked V2 records."""

import argparse
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from scripts.scheme_identity import normalized_title, resolve_identity, urls, without_region
from scripts.scheme_source_reviews import COMPONENT_REVIEWS, DOCUMENT_NOTES, DOCUMENT_REVIEWS
from services.scheme_revisions import checklist, document_id
from services.studio_catalog import CATALOG_PATH, load_directory_source
from utils import generate_slug


DOCUMENT_EQUIVALENTS = {
    "disabilitycertificatesadaremudid": "udiddisabilitycertificate",
    "motherchildprotectionmcpcard": "mcpcard",
    "motherandchildprotectionmcpcard": "mcpcard",
    "bankaccountpassbookaadhaarseeded": "aadhaarlinkedbankpassbook",
    "doctorsprescription": "doctorprescription",
    "mothersaadhaarcard": "aadhaarcardofmother",
    "mothersaadhaarlinkedbankpassbook": "aadhaarlinkedbankpassbook",
}


def document_key(name):
    key = normalized_title(name)
    return DOCUMENT_EQUIVALENTS.get(key, key)


def merge_documents(record, incoming):
    baseline = {key: value for key, value in record.items()
                if key not in {"reconciled_documents", "document_provenance", "document_conflict_ids", "document_guidance"}}
    current, _ = checklist(baseline)
    baseline_optional = {
        document_key(item["name"]): item["optional"] for item in record.get("required_documents") or []
        if isinstance(item, dict) and isinstance(item.get("optional"), bool)
    }
    existing = {document_key(item["name"]["en"] or item["name"]["te"]): item for item in current}
    provenance = {item["id"]: [{"source": "studio_master"}] for item in current}
    candidates = {}
    conflicts = {}
    for title, source in incoming:
        url = source.get("official_website") or source.get("source_url")
        for value in source.get("required_documents") or []:
            row = {"name": value} if isinstance(value, str) else value
            key = document_key(row["name"])
            claim = {"source": "v2_catalog", "scheme_title": title, "source_url": url,
                     "document": row}
            if prior := existing.get(key):
                provenance[prior["id"]].append(claim)
                mandatory = prior["mandatory"]
                if mandatory is None and key in baseline_optional:
                    mandatory = not baseline_optional[key]
                if mandatory is not None and "optional" in row and mandatory == row["optional"]:
                    conflict = conflicts.setdefault(prior["id"], {
                        "id": prior["id"], "document": prior["name"], "reason": "required_vs_optional", "claims": [],
                    })
                    conflict["claims"].append(claim)
                continue
            candidate = candidates.setdefault(key, {
                "id": row.get("id") or document_id(row["name"]),
                "name": {"en": row["name"], "te": row.get("name_te") or None},
                "verification_status": "verification_pending", "sources": [],
            })
            candidate["sources"].append(claim)
    for row in candidates.values():
        optionality = {claim["document"].get("optional") for claim in row["sources"]} - {None}
        if len(optionality) > 1:
            conflicts[row["id"]] = {
                "id": row["id"], "document": row["name"], "reason": "required_vs_optional", "claims": row["sources"],
            }
    return provenance, list(candidates.values()), list(conflicts.values())


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
        if name in existing and existing[name].get("directory_entry") and (
            record.get("operations_reviewed", "") > existing[name].get("operations_reviewed", "")
        ):
            catalog[name]["operations"] = record["operations"]
            catalog[name]["operations_reviewed"] = record["operations_reviewed"]
        if name not in existing:
            catalog[name] = record
        elif not existing[name].get("directory_entry"):
            catalog[name].pop("directory_entry", None)
            # Preserve the legacy ID and the surface it is already available on.
            if "slug" not in existing[name]:
                catalog[name].pop("slug", None)
    url_owners = defaultdict(set)
    for name, record in catalog.items():
        for url in urls(record):
            url_owners[url].add(name)
    report = {"matched": [], "pending_review": [], "checklist_reconciliation": [], "programme_components": []}
    components = defaultdict(list)
    groups = defaultdict(list)
    for title, record in v2.items():
        if title in COMPONENT_REVIEWS:
            parent, reviewed = COMPONENT_REVIEWS[title]
            if parent in catalog and normalized_title(record.get("level") or "") == normalized_title(catalog[parent].get("level") or ""):
                item = {**reviewed, "search_title": title}
                components[parent].append(item)
                report["programme_components"].append({
                    "catalog_title": parent, **item, "v2_document_claims": record.get("required_documents") or [],
                })
                continue
        name, method, source, candidates = resolve_identity(title, record, catalog, url_owners)
        if name is None:
            region = record.get("level") or ""
            identity_key = normalized_title(region) + ":" + normalized_title(without_region(title, region))
            report["pending_review"].append({
                "title": title, "identity_key": identity_key, "reason": method,
                "candidates": candidates, "v2_record": record,
            })
            continue
        groups[name].append((title, record))
        report["matched"].append({
            "v2_title": title, "catalog_title": name,
            "catalog_id": catalog[name].get("slug") or generate_slug(name),
            "method": method, "identity_source": source,
            "v2_documents": record.get("required_documents") or [],
            "v2_source_url": record.get("official_website") or record.get("source_url"),
        })
    for name, rows in groups.items():
        record = catalog[name]
        aliases = list(dict.fromkeys([*(record.get("aliases") or []), *(title for title, _ in rows if title != name)]))
        provenance, documents, conflicts = merge_documents(record, rows)
        catalog[name] = {**record, "document_provenance": provenance}
        if aliases:
            catalog[name]["aliases"] = aliases
        if documents:
            catalog[name]["reconciled_documents"] = documents
        else:
            catalog[name].pop("reconciled_documents", None)
        guidance = DOCUMENT_REVIEWS.get(name, {})
        resolved = [{**conflict, "guidance": guidance[conflict["id"]]} for conflict in conflicts if conflict["id"] in guidance]
        conflicts = [conflict for conflict in conflicts if conflict["id"] not in guidance]
        if guidance:
            catalog[name]["document_guidance"] = guidance
            for language, key in (("en", "simplified"), ("te", "telugu")):
                catalog[name][key] = {**(catalog[name].get(key) or {}), "documents": DOCUMENT_NOTES[name][language]}
        if conflicts:
            catalog[name]["document_conflict_ids"] = [conflict["id"] for conflict in conflicts]
        else:
            catalog[name].pop("document_conflict_ids", None)
        if documents or conflicts or resolved:
            report["checklist_reconciliation"].append({
                "catalog_title": name, "document_provenance": provenance,
                "additional_documents": documents, "conflicts": conflicts, "resolved_conflicts": resolved,
            })
    for name, rows in components.items():
        catalog[name]["programme_components"] = rows
    report["summary"] = {
        "catalog_records": len(catalog),
        "v2_records": len(v2),
        "v2_records_with_documents": sum(bool(row.get("required_documents")) for row in v2.values()),
        "matched": len(report["matched"]),
        "alias_matches": sum(row["method"] != "exact_title" for row in report["matched"]),
        "pending_review": len(report["pending_review"]),
        "programme_components": len(report["programme_components"]),
        "additional_document_candidates": sum(len(row["additional_documents"]) for row in report["checklist_reconciliation"]),
        "document_conflicts": sum(len(row["conflicts"]) for row in report["checklist_reconciliation"]),
        "resolved_document_conflicts": sum(len(row["resolved_conflicts"]) for row in report["checklist_reconciliation"]),
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
    from scripts.consolidate_catalog import consolidate
    manifest = json.loads((root/"data/studio/v2_resolution.json").read_text(encoding="utf-8-sig"))
    catalog, report, archive = consolidate(
        read_records(args.catalog), load_directory_source(args.directory),
        read_records(args.v2_master), manifest,
    )
    write_json(args.review_output, report)
    write_json(args.output, catalog)
    write_json(root/"data/backups/unlinked_audit_archive.json", {"reviewed":manifest["reviewed"],"records":archive})
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
