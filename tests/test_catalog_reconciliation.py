import json
from pathlib import Path

from scripts.merge_schemes import reconcile_catalog
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
    assert catalog["Other Scheme"]["required_documents"] == ["Address proof"]
    assert report["matched"][0]["document_action"] == "review_checklist_difference"
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
