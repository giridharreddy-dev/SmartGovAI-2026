"""Apply explicitly reviewed operation patches without replacing the baseline."""

import json
import unicodedata
from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Literal

from pydantic import HttpUrl, field_validator, model_validator

from services.scheme_operations import (
    Application, Benefits, Document, Eligibility, Record, SchemeOperations, Section, SectionStatus,
)
from utils import generate_slug

REVISION_PATH = Path("data/studio/operation_revisions.json")
SECTIONS = ("eligibility", "required_documents", "benefits", "application_process")


class ReviewedRevision(Record):
    lead_id: str
    scheme_id: str
    status: Literal["verified"]
    reviewed_on: str
    source_url: HttpUrl
    eligibility: Eligibility | None = None
    required_documents: list[Document] | None = None
    benefits: Benefits | None = None
    application_process: Application | None = None
    section_statuses: dict[Section, SectionStatus] | None = None

    @field_validator("reviewed_on")
    @classmethod
    def iso_date(cls, value):
        return date.fromisoformat(value).isoformat()

    @field_validator("source_url")
    @classmethod
    def https_source(cls, value):
        return Application.official_https(value)

    @model_validator(mode="after")
    def review_contract(self):
        ids = [document.id for document in (self.required_documents or [])]
        if any(not item for item in ids) or len(ids) != len(set(ids)):
            raise ValueError("Changed document requirements need unique, stable IDs")
        if not self.lead_id or not self.scheme_id or not (revision_fields(self) or self.section_statuses):
            raise ValueError("A reviewed revision needs a lead, a scheme and at least one supported change")
        return self


def read_revisions(root):
    path = Path(root) / REVISION_PATH
    if not path.is_file():
        return []
    return [ReviewedRevision.model_validate(row) for row in json.loads(path.read_text(encoding="utf-8"))["revisions"]]


def revision_fields(revision):
    changes = {}
    for name in SECTIONS:
        value = getattr(revision, name)
        if not value:
            continue
        if name == "required_documents":
            changes[name] = [item.model_dump(mode="json", exclude_none=True) for item in value]
        else:
            block = value.model_dump(mode="json", exclude_unset=True, exclude_none=True)
            if filled := {key: item for key, item in block.items() if item != []}:
                changes[name] = filled
    return changes


def document_id(name):
    key = " ".join(unicodedata.normalize("NFKC", name).casefold().split())
    return "d-" + sha256(key.encode()).hexdigest()[:20]


def catalog_document_lists(scheme):
    """Return legacy and structured checklists in the same ID representation."""
    legacy = []
    for item in scheme.get("required_documents") or []:
        row = {"name": item} if isinstance(item, str) else item
        if isinstance(row, dict) and row.get("name"):
            legacy.append({
                "id": row.get("id") or document_id(row["name"]),
                "name": {"en": row["name"], "te": row.get("name_te") or None},
                "purpose": None, "mandatory": False if row.get("optional") is True else None,
            })
    structured = [
        dict(item, id=item.get("id") or document_id(item["name"].get("en") or item["name"]["te"]))
        for item in (scheme.get("operations") or {}).get("required_documents", [])
    ]
    return legacy, structured


def checklist(scheme):
    if scheme.get("canonical"):
        from services.canonical_catalog import canonical_checklist
        return canonical_checklist(scheme["canonical"]), scheme.get("checklist_aliases") or {}
    legacy, structured = catalog_document_lists(scheme)
    effective = {item["id"]: item for item in legacy + structured}
    aliases = scheme.get("checklist_aliases")
    if aliases is None:
        aliases = previous_checklist_keys(legacy, structured)
    provenance = scheme.get("document_provenance") or {}
    conflicts = set(scheme.get("document_conflict_ids") or [])
    for item_id, item in effective.items():
        if item_id in provenance:
            effective[item_id] = dict(item, sources=provenance[item_id])
        if item_id in conflicts:
            effective[item_id] = dict(effective[item_id], verification_status="verification_pending", mandatory=None)
    for item in scheme.get("reconciled_documents") or []:
        effective.setdefault(item["id"], item)
    for item_id, guidance in (scheme.get("document_guidance") or {}).items():
        if item_id in effective:
            effective[item_id] = {**effective[item_id], **guidance}
    return list(effective.values()), aliases


def previous_checklist_keys(legacy, structured):
    aliases = {str(i): item["id"] for i, item in enumerate(legacy)}
    aliases.update({"ops:" + (item["name"]["en"] or item["name"]["te"]): item["id"] for item in structured})
    return aliases


def section_statuses(scheme):
    operations = scheme.get("operations") or {}
    statuses = scheme.get("section_status_overrides") or {}
    documents, _ = checklist(scheme)
    baseline_keys = {"eligibility": "eligibility", "benefits": "benefits", "application_process": "steps"}
    result = {}
    for block in SECTIONS:
        content = operations.get(block) or {}
        typed = bool(content) if isinstance(content, list) else any(
            value is not None and value != [] for value in content.values()
        )
        if block == "required_documents" and typed:
            reviewed_ids = {item["id"] for item in catalog_document_lists(scheme)[1]}
            typed = all(item["id"] in reviewed_ids for item in documents)
        default = "verified" if typed and scheme.get("operations_reviewed") else "verification_pending"
        status = statuses.get(block, default)
        if block == "required_documents":
            if documents and all(item.get("verification_status") == "official_source_unspecified" for item in documents):
                status = "official_source_unspecified"
            elif status == "verified" and (not documents or any(
                item.get("verification_status") == "verification_pending" for item in documents
            )):
                status = "verification_pending"
            elif default == "verified" and status == "official_source_unspecified":
                status = default
        elif status == "verified" and not typed and not any(
            (scheme.get(language) or {}).get(baseline_keys[block]) for language in ("simplified", "telugu")
        ):
            status = "verification_pending"
        result[block] = status
    return result


def apply_revisions(schemes, revisions):
    if not revisions:
        return schemes
    catalog = dict(schemes)
    names = {(item.get("slug") or generate_slug(name)): name for name, item in catalog.items()}
    seen = set()
    for revision in revisions:
        name = names.get(revision.scheme_id)
        if not name or revision.lead_id in seen:
            raise ValueError(f"Unknown scheme or repeated revision lead: {revision.lead_id}")
        seen.add(revision.lead_id)
        current = dict(catalog[name])
        had_canonical = current.pop("canonical", None) is not None
        if revision.reviewed_on < (current.get("operations_reviewed") or ""):
            raise ValueError(f"Revision for {name} predates the existing operational review")
        legacy, structured = catalog_document_lists(current)
        aliases = current.get("checklist_aliases", previous_checklist_keys(legacy, structured))
        operations = {key: value for key, value in (current.get("operations") or {}).items()}
        changes = revision_fields(revision)
        for block in ("eligibility", "benefits", "application_process"):
            operations[block] = {**operations.get(block, {}), **changes.get(block, {})}
        documents = {item["id"]: item for item in structured}
        changed_documents = changes.get("required_documents", [])
        for item in changed_documents:
            previous = documents.get(item["id"]) or next((doc for doc in legacy if doc["id"] == item["id"]), {})
            documents[item["id"]] = {**previous, **item}
        operations["required_documents"] = list(documents.values())
        validated = SchemeOperations.model_validate(operations).model_dump(mode="json")
        statuses = {**(current.get("section_status_overrides") or {}), **(revision.section_statuses or {})}
        resolved_document_ids = {item["id"] for item in changed_documents}
        catalog[name] = {
            **current,
            "operations": validated,
            "operations_reviewed": revision.reviewed_on,
            "operations_source": str(revision.source_url),
            "section_status_overrides": statuses,
            "checklist_aliases": aliases,
            "document_guidance": {
                item_id: guidance for item_id, guidance in (current.get("document_guidance") or {}).items()
                if item_id not in resolved_document_ids
            },
            "document_conflict_ids": [
                item_id for item_id in current.get("document_conflict_ids") or [] if item_id not in resolved_document_ids
            ],
        }
        if had_canonical:
            from services.canonical_catalog import canonicalize
            catalog[name]["canonical"] = canonicalize(name, catalog[name])
    return catalog
