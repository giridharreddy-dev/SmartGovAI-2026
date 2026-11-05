"""Consolidate audited V2 identities into the bundled canonical catalog."""
import argparse
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

from scripts.merge_schemes import merge_documents, read_records, reconcile_catalog, write_json
from services.canonical_catalog import canonicalize, runtime_record, PENDING
from services.scheme_revisions import catalog_document_lists, checklist
from services.studio_catalog import load_directory_source
from utils import generate_slug


def consolidate(existing, directory, v2, manifest):
    runtime = {name: deepcopy(runtime_record(row)) for name, row in existing.items()}
    baseline = {name: {doc["id"] for doc in checklist(row)[0]} for name, row in runtime.items()}
    for row in runtime.values():
        row.pop("canonical", None)
    decisions = {row["source_title"]: row for row in manifest["records"]}
    catalog, report = reconcile_catalog(runtime, directory, {key: value for key, value in v2.items() if key not in decisions})
    if len(decisions) != len(manifest["records"]) or not set(decisions) <= set(v2):
        raise ValueError("Disposition titles must be unique and present in the source")
    archive, dispositions = [], []
    groups = defaultdict(list)
    for title, decision in decisions.items():
        if decision["action"] == "promote" and decision["target"] not in catalog:
            name = decision["target"]
            catalog[name] = {
                "slug": "welfare-" + generate_slug(name),
                "level": decision.get("region") or v2[title].get("level") or "National",
                "category": "Health", "sector": "health", "telugu_name": "",
                "source_name": "Official programme source", "official_website": decision["source_url"],
                "source_reviewed": manifest["reviewed"], "directory_entry": True,
                "required_documents": [], "simplified": {"description": PENDING["en"]},
                "telugu": {"description": PENDING["te"]},
            }
    for title, decision in decisions.items():
        action = decision["action"]
        if action == "archive":
            archive.append({**decision, "original_record": v2[title]})
        else:
            name = decision["target"]
            if name not in catalog:
                raise ValueError(f"Missing target for {title}")
            row = catalog[name]
            if action in ("promote", "alias"):
                row["aliases"] = list(dict.fromkeys([*(row.get("aliases") or []), *([title] if title != name else [])]))
                groups[name].append((title, v2[title]))
            elif action == "component":
                parts = row.setdefault("programme_components", [])
                part = next((p for p in parts if p["id"] == decision["component_id"]), None)
                if part is None:
                    part = {
                        "id": decision["component_id"], "title": decision["title"],
                        "summary": PENDING.copy(), "specific_rules": "verification_pending",
                        "source_url": decision["source_url"], "search_title": title, "source_variants": [],
                    }
                    parts.append(part)
                variants = part.setdefault("source_variants", [])
                if not any(item["title"] == title for item in variants):
                    variants.append({"title": title, "region": v2[title].get("level"),
                                     "required_documents": v2[title].get("required_documents") or [],
                                     "source_url": decision["source_url"], "status": "verification_pending"})
                row["keywords"] = list(dict.fromkeys([*(row.get("keywords") or []), title]))
            else:
                raise ValueError(f"Unknown action for {title}")
        dispositions.append(decision)
    for name, sources in groups.items():
        row = catalog[name]
        # Preserve all prior claims while incorporating additional aliases.
        prior, _ = checklist(row)
        temporary = deepcopy(row)
        temporary["required_documents"] = [
            {"id": item["id"], "name": item["name"].get("en") or item["name"].get("te") or "",
             "name_te": item["name"].get("te") or "", "optional": item.get("mandatory") is False}
            for item in prior
        ]
        provenance, additions, _ = merge_documents(temporary, sources)
        legacy_docs, structured_docs = catalog_document_lists(row)
        baseline_ids = {item["id"] for item in legacy_docs + structured_docs}
        for key in list(row.get("document_provenance") or {}):
            if key not in baseline_ids:
                row["document_provenance"][key] = [
                    claim for claim in row["document_provenance"][key] if claim.get("source") != "studio_master"
                ]
        for key, claims in provenance.items():
            old = row.setdefault("document_provenance", {}).setdefault(key, [])
            for claim in claims:
                if claim.get("source") == "studio_master" and key not in baseline_ids:
                    continue
                if claim not in old:
                    old.append(claim)
        effective = {item["id"]: item for item in row.get("reconciled_documents") or []}
        for item in additions:
            effective.setdefault(item["id"], item)
        row["reconciled_documents"] = list(effective.values())
    result = {name: canonicalize(name, row) for name, row in catalog.items()}
    if len({row["id"] for row in result.values()}) != len(result):
        raise ValueError("Duplicate canonical IDs")
    for name, ids in baseline.items():
        if not ids <= {doc["id"] for doc in result[name]["required_documents"]}:
            raise ValueError(f"Documents removed from {name}")
    handled = {r["v2_title"] for r in report["matched"]} | {r["search_title"] for r in report["programme_components"]} | set(decisions)
    if set(v2) - handled:
        raise ValueError("Source rows without a disposition")
    counts = Counter(row["action"] for row in dispositions)
    report["pending_review"] = []
    report["dispositions"] = dispositions
    report["summary"].update(
        catalog_records=len(result), v2_records=len(v2), v2_records_with_documents=sum(bool(row.get("required_documents")) for row in v2.values()),
        pending_review=0, archived=counts["archive"], promoted=counts["promote"],
        programme_components=sum(len(row["programme_components"]) for row in result.values()),
        aliases=sum(len(row["aliases"]) for row in result.values()),
    )
    return result, report, archive


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("v2_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--review-output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((root/"data/studio/v2_resolution.json").read_text(encoding="utf-8-sig"))
    result, report, archive = consolidate(
        read_records(root/"data/merged_schemes.json"), load_directory_source(root/"data/studio/welfare.json"),
        read_records(args.v2_source), manifest)
    write_json(args.output, result)
    write_json(root/"data/backups/unlinked_audit_archive.json", {"reviewed":manifest["reviewed"],"records":archive})
    write_json(args.review_output, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
