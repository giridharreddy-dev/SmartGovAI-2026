"""Canonical offline catalog contract and compatibility for existing portal callers."""

import json
from copy import deepcopy
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator
from services.scheme_revisions import checklist, section_statuses
from utils import generate_slug

PENDING = {
    "en": "Details are being verified against official guidance. Confirm with the official portal before applying.",
    "te": "వివరాలు అధికారిక మార్గదర్శకాల ఆధారంగా ధృవీకరించబడుతున్నాయి. దరఖాస్తు చేయడానికి ముందు అధికారిక పోర్టల్‌ను తనిఖీ చేయండి.",
}


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Localized(Record):
    en: str
    te: str


class Criterion(Record):
    field: str
    rule: str
    value: str


class Eligibility(Record):
    status: Literal["verified", "verification_pending"]
    summary: Localized
    criteria: list[Criterion]


class RequiredDocument(Record):
    id: str
    name: Localized
    status: Literal["mandatory", "optional_spot_generated", "facility_dependent", "verification_pending"]
    source_provenance: Literal["official_guideline", "v2_catalog", "studio_master"]
    verification_note: Localized
    sources: list[dict] = []


class Benefits(Record):
    status: Literal["verified", "verification_pending"]
    financial_cap: str
    cashless: bool | None
    summary: Localized


class Steps(Record):
    en: list[str]
    te: list[str]


class Application(Record):
    status: Literal["verified", "verification_pending"]
    mode: str
    portal_url: str
    steps: Steps


class Component(Record):
    id: str
    title: Localized
    specific_rules: str
    summary: Localized
    source_url: str
    search_title: str
    source_variants: list[dict] = []


class CanonicalScheme(Record):
    id: str
    title: Localized
    title_status: Literal["verified", "verification_pending"]
    region: str
    aliases: list[str]
    category: str
    source_url: str
    eligibility: Eligibility
    required_documents: list[RequiredDocument]
    benefits: Benefits
    application_process: Application
    programme_components: list[Component]
    legacy: dict

    @model_validator(mode="after")
    def stable_document_ids(self):
        ids = [doc.id for doc in self.required_documents]
        if len(ids) != len(set(ids)) or any(not value for value in ids):
            raise ValueError("Document IDs must be nonempty and unique")
        for doc in self.required_documents:
            if "PM-JAY (National Health Cover)" in self.title.en and doc.id in {"abha-id", "d-63c51733c29672f6bf9b"}:
                if doc.status != "optional_spot_generated":
                    raise ValueError("PM-JAY intake card guidance must remain optional")
            if "Control of Blindness (NPCBVI)" in self.title.en and "aadhaar" in doc.name.en.casefold():
                if doc.status != "facility_dependent":
                    raise ValueError("NPCBVI identity guidance must remain facility dependent")
        return self


def localized(value, fallback=None):
    value = value or {}
    return {"en": value.get("en") or (fallback or PENDING)["en"],
            "te": value.get("te") or (fallback or PENDING)["te"]}


def canonicalize(name, record):
    if "legacy" in record:
        return CanonicalScheme.model_validate(record).model_dump()
    row = deepcopy(record)
    operations = row.get("operations") or {}
    statuses = section_statuses(row)
    documents, aliases = checklist(row)
    row["checklist_aliases"] = aliases
    docs = []
    for doc in documents:
        status = doc.get("status")
        if status == "optional_at_initial_verification":
            status = "optional_spot_generated"
        elif status == "facility_specific":
            status = "facility_dependent"
        elif doc.get("verification_status") == "verified" or (
            row.get("operations_reviewed") and doc["id"] in {d.get("id") for d in operations.get("required_documents") or []}
        ):
            status = "mandatory" if doc.get("mandatory") else "facility_dependent"
        else:
            status = "verification_pending"
        sources = doc.get("sources") or []
        provenance = "official_guideline" if status != "verification_pending" else (
            "v2_catalog" if any(source.get("source") == "v2_catalog" for source in sources) else "studio_master")
        docs.append({
            "id": doc["id"], "name": {"en": doc["name"].get("en") or "", "te": doc["name"].get("te") or ""},
            "status": status, "source_provenance": provenance,
            "verification_note": localized(doc.get("purpose")), "sources": sources,
        })

    if name == "Ayushman Bharat PM-JAY (National Health Cover)":
        docs.append({
            "id": "abha-id", "name": {"en": "ABHA ID (if available)", "te": "ABHA గుర్తింపు (ఉంటే)"},
            "status": "optional_spot_generated", "source_provenance": "official_guideline",
            "verification_note": {
                "en": "ABHA is a separate digital health account and does not prove PM-JAY eligibility. Ask the hospital desk about beneficiary verification and card generation.",
                "te": "ABHA ప్రత్యేక డిజిటల్ ఆరోగ్య ఖాతా. ఇది PM-JAY అర్హతకు రుజువు కాదు. లబ్ధిదారుల ధృవీకరణ, కార్డు జారీ గురించి ఆసుపత్రి సహాయ కేంద్రంలో అడగండి.",
            }, "sources": [{"source":"official_guideline","source_url":"https://abdm.gov.in/strapicms/uploads/ABHA_Brochure_Piano_final_b972459053.pdf"}],
        })
    if "Control of Blindness (NPCBVI)" in name:
        for doc in docs:
            if "aadhaar" in doc["name"]["en"].casefold():
                doc["status"] = "facility_dependent"
                doc["verification_note"] = {
                    "en": "Ask the eye facility which photo ID it accepts, such as Aadhaar, voter ID or passport. National guidance does not set one universal identification checklist.",
                    "te": "ఆధార్, ఓటరు గుర్తింపు లేదా పాస్‌పోర్ట్ వంటి ఏ ఫోటో గుర్తింపును అంగీకరిస్తారో నేత్ర వైద్య కేంద్రాన్ని అడగండి. జాతీయ మార్గదర్శకాల్లో అందరికీ ఒకే గుర్తింపు జాబితా లేదు.",
                }

    def summary(section, legacy_key):
        typed = operations.get(section) or {}
        fields = {
            "eligibility": ["target_group", "criteria", "exclusions", "income_ceiling", "age_range", "residence"],
            "benefits": ["coverage_amount", "coverage_type", "details", "disbursement"],
        }[section]
        result = {}
        for lang, key in (("en", "simplified"), ("te", "telugu")):
            parts = []
            for field in fields:
                values = typed.get(field)
                for value in values if isinstance(values, list) else [values]:
                    if isinstance(value, dict) and value.get(lang):
                        parts.append(value[lang])
            result[lang] = "\n".join(parts) or (row.get(key) or {}).get(legacy_key) or PENDING[lang]
        return result

    application = operations.get("application_process") or {}
    steps = {}
    for lang, key in (("en", "simplified"), ("te", "telugu")):
        steps[lang] = [item[lang] for item in application.get("steps") or [] if item.get(lang)]
        if not steps[lang]:
            old = (row.get(key) or {}).get("steps")
            steps[lang] = old.split("\n") if old else [PENDING[lang]]
    criteria = []
    for field, label in (("age_range", "age"), ("income_ceiling", "income"), ("caste_category", "category"), ("residence", "residence")):
        value = (operations.get("eligibility") or {}).get(field)
        if value:
            criteria.append({"field": label, "rule": "official_guidance", "value": json.dumps(value, ensure_ascii=False)})
    data = {
        "id": row.get("slug") or generate_slug(name),
        "title": {"en": name, "te": row.get("telugu_name") or ""},
        "title_status": "verified" if row.get("telugu_name") else "verification_pending",
        "region": row.get("level") or "National", "aliases": row.get("aliases") or [],
        "category": row.get("category") or "Social Welfare",
        "source_url": row.get("official_website") or row.get("source_url") or "",
        "eligibility": {"status": "verified" if statuses["eligibility"] == "verified" else "verification_pending",
                        "summary": summary("eligibility", "eligibility"), "criteria": criteria},
        "required_documents": docs,
        "benefits": {
            "status": "verified" if statuses["benefits"] == "verified" else "verification_pending",
            "financial_cap": ((operations.get("benefits") or {}).get("coverage_amount") or {}).get("en") or "verification_pending",
            "cashless": (operations.get("benefits") or {}).get("cashless"),
            "summary": summary("benefits", "benefits"),
        },
        "application_process": {
            "status": "verified" if statuses["application_process"] == "verified" else "verification_pending",
            "mode": (application.get("mode") or {}).get("en") or "verification_pending",
            "portal_url": application.get("official_url") or row.get("official_website") or row.get("source_url") or "",
            "steps": steps,
        },
        "programme_components": [
            {"id": item["id"], "title": {"en": item["title"].get("en") or "", "te": item["title"].get("te") or ""},
             "specific_rules": item.get("specific_rules") or "verification_pending",
             "summary": localized(item.get("summary")), "source_url": item.get("source_url") or "",
             "search_title": item.get("search_title") or item["title"].get("en") or "",
             "source_variants": item.get("source_variants") or []}
            for item in row.get("programme_components") or []
        ],
        "legacy": row,
    }
    return CanonicalScheme.model_validate(data).model_dump()


def runtime_record(record):
    if "legacy" not in record:
        return record
    canonical = CanonicalScheme.model_validate(record).model_dump()
    row = deepcopy(canonical["legacy"])
    row["canonical"] = canonical
    row["slug"] = canonical["id"]
    row["aliases"] = canonical["aliases"]
    row["programme_components"] = canonical["programme_components"]
    return row


def canonical_checklist(canonical):
    return [{
        "id": doc["id"], "name": doc["name"],
        "mandatory": True if doc["status"] == "mandatory" else False if doc["status"] == "optional_spot_generated" else None,
        "status": "optional_at_initial_verification" if doc["status"] == "optional_spot_generated" else
                  "facility_specific" if doc["status"] == "facility_dependent" else doc["status"],
        "verification_status": "verification_pending" if doc["status"] == "verification_pending" else "verified",
        "purpose": doc["verification_note"], "sources": doc["sources"],
        "source_provenance": doc["source_provenance"],
    } for doc in canonical["required_documents"]]
