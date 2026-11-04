import json
from pathlib import Path

from scripts.merge_schemes import reconcile_catalog
from services.scheme_revisions import checklist
from services.studio_catalog import CATALOG_PATH, load_master_catalog


def test_reconcile_preserves_baseline_and_flags_unlinked_titles():
    original = {"Example Scheme": {
        "level": "National", "required_documents": ["ID"],
        "simplified": {"eligibility": "Baseline rule", "steps": "Apply"},
    }}
    directory = {
        "Example Scheme": {"simplified": {"eligibility": "", "benefits": "New details"}},
        "Other Scheme": {"level": "Andhra Pradesh", "required_documents": []},
    }
    v2 = {
        "Example-Scheme": {"level": "National", "required_documents": ["Different ID"]},
        "Other Scheme": {"level": "Andhra Pradesh", "required_documents": ["Address proof"]},
        "Unlinked": {"level": "National", "required_documents": ["Certificate"]},
    }
    catalog, report = reconcile_catalog(original, directory, v2)
    assert catalog["Example Scheme"]["required_documents"] == ["ID"]
    assert catalog["Example Scheme"]["simplified"] == {
        "eligibility": "Baseline rule", "steps": "Apply", "benefits": "New details",
    }
    docs, _ = checklist(catalog["Other Scheme"])
    assert docs[0]["name"]["en"] == "Address proof"
    assert docs[0]["verification_status"] == "verification_pending"
    docs, _ = checklist(catalog["Example Scheme"])
    assert [doc["name"]["en"] for doc in docs] == ["ID", "Different ID"]
    assert [doc["sources"][0]["source"] for doc in docs] == ["studio_master", "v2_catalog"]
    assert report["pending_review"][0]["v2_record"]["required_documents"] == ["Certificate"]
    assert "Unlinked" not in catalog


def test_catalog_reads_only_the_explicit_master(tmp_path):
    path = tmp_path / CATALOG_PATH
    path.parent.mkdir()
    path.write_text(json.dumps({"Example": {"required_documents": ["ID"]}}), encoding="utf-8")
    (path.parent / "zzz_scraped.json").write_text(
        json.dumps({"Example": {"required_documents": []}, "Unlinked": {}}), encoding="utf-8"
    )
    catalog = load_master_catalog(tmp_path)
    assert list(catalog) == ["Example"]
    assert catalog["Example"]["required_documents"] == ["ID"]


def test_bundled_master_contains_both_catalog_subsets():
    catalog = load_master_catalog(Path(__file__).resolve().parents[1])
    assert len(catalog) == 208
    assert sum(bool(row.get("directory_entry")) for row in catalog.values()) == 75
    assert sum(bool(row.get("required_documents")) for row in catalog.values()) == 133


def test_url_match_requires_title_evidence_and_same_region():
    page = "https://example.gov.in/schemes/mobile"
    master = {
        "Mobile Health Outreach Scheme": {"level": "National", "official_website": page, "required_documents": []},
    }
    v2 = {
        "Dr. Mobile Health Outreach Yojana": {"level": "National", "application_url": page},
        "Mobile Health Outreach Scheme (Second Child)": {"level": "National", "source_url": page},
        "Mobile Health Outreach Scheme": {"level": "Andhra Pradesh", "source_url": page},
        "Dental Procedures": {"level": "National", "source_url": page},
        "Mobile Health Outreach Pilot": {"level": "National", "source_url": "https://example.gov.in/other"},
    }
    catalog, report = reconcile_catalog(master, {}, v2)
    assert catalog["Mobile Health Outreach Scheme"]["aliases"] == ["Dr. Mobile Health Outreach Yojana"]
    assert report["matched"][0]["method"] == "scheme_url_and_title"
    assert len(report["pending_review"]) == 4


def test_document_union_keeps_checklist_keys_and_flags_conflicting_claims():
    title = "Example Health Scheme"
    master = {title: {"level": "National", "required_documents": [{"name": "Photo ID", "optional": False}]}}
    v2 = {
        title: {"level": "National", "required_documents": [{"name": "Photo ID", "optional": True}, "Address proof"]},
        title + " (National)": {"level": "National", "required_documents": [{"name": "Photo ID", "optional": True}]},
    }
    catalog, report = reconcile_catalog(master, {}, v2)
    docs, aliases = checklist(catalog[title])
    assert aliases["0"] == docs[0]["id"]
    assert docs[0]["mandatory"] is None
    assert docs[0]["verification_status"] == "verification_pending"
    assert docs[1]["name"]["en"] == "Address proof"
    assert len(report["checklist_reconciliation"][0]["conflicts"]) == 1
    assert len(docs[0]["sources"]) == 3
    assert reconcile_catalog(catalog, {}, v2) == (catalog, report)

def test_official_review_guidance_and_component_parents_are_in_master():
    catalog = load_master_catalog(Path(__file__).resolve().parents[1])
    pmjay = catalog["Ayushman Bharat PM-JAY (National Health Cover)"]
    docs, _ = checklist(pmjay)
    card = next(item for item in docs if item["name"]["en"] == "Ayushman Card")
    assert card["status"] == "optional_at_initial_verification"
    assert card["mandatory"] is False
    assert "70+" in pmjay["simplified"]["documents"]
    assert pmjay["programme_components"][0]["id"] == "senior-citizen-70-plus"

    eye = catalog["National Programme for Control of Blindness (NPCBVI)"]
    docs, _ = checklist(eye)
    assert docs[0]["status"] == "facility_specific"
    assert docs[0]["mandatory"] is None
    assert not eye.get("document_conflict_ids")

    assert sum(len(item.get("programme_components") or []) for item in catalog.values()) == 5
    dialysis = catalog["Pradhan Mantri National Dialysis Programme"]
    assert {item["id"] for item in dialysis["programme_components"]} == {"haemodialysis", "peritoneal-dialysis"}
    assert all("required_documents" not in item for item in dialysis["programme_components"])
