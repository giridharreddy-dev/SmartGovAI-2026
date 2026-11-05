import pytest
from pydantic import ValidationError

from scripts.apply_scheme_revision import apply_file
from services.scheme_revisions import REVISION_PATH, ReviewedRevision, checklist, read_revisions, section_statuses


def test_reviewed_benefit_patch_preserves_requirements_and_old_checklist_keys(tmp_path):
    catalog = {"Example": {
        "slug": "example",
        "required_documents": [{"id": "bank-details", "name": "Bank details"}],
        "operations": {
            "eligibility": {"income_ceiling": {"en": "Existing income rule"}},
            "required_documents": [{"id": "identity", "name": {"en": "Identity proof"}}],
            "benefits": {"coverage_amount": {"en": "Old amount"}, "cashless": True},
            "application_process": {"mode": {"en": "Online"}},
        },
        "operations_reviewed": "2026-11-01",
    }}
    update = {
        "lead_id": "pib:example", "scheme_id": "example", "status": "verified",
        "reviewed_on": "2026-11-05", "source_url": "https://example.gov.in/revision",
        "benefits": {"coverage_amount": {"en": "Updated amount"}}, "required_documents": [],
        "section_statuses": {"required_documents": "official_source_unspecified"},
    }
    with pytest.raises(ValidationError):
        ReviewedRevision.model_validate(dict(update, status="pending_human_verification"))
    revision = ReviewedRevision.model_validate(update)
    preview = apply_file(tmp_path, catalog, revision)
    assert not (tmp_path / REVISION_PATH).exists()
    assert preview["operations"]["benefits"]["coverage_amount"]["en"] == "Updated amount"
    assert preview["operations"]["benefits"]["cashless"] is True
    assert preview["operations"]["eligibility"]["income_ceiling"]["en"] == "Existing income rule"
    assert [item["id"] for item in checklist(preview)[0]] == ["bank-details", "identity"]
    assert catalog["Example"]["operations"]["benefits"]["coverage_amount"]["en"] == "Old amount"

    apply_file(tmp_path, catalog, revision, write=True)
    assert read_revisions(tmp_path) == [revision]
    changed_documents = ReviewedRevision.model_validate(dict(
        update, lead_id="pib:documents", benefits=None, section_statuses=None,
        required_documents=[
            {"id": "identity", "name": {"en": "Updated identity proof", "te": "గుర్తింపు పత్రం"}},
            {"id": "residence", "name": {"en": "Residence proof"}},
        ],
    ))
    updated = apply_file(tmp_path, catalog, changed_documents, write=True)
    documents, aliases = checklist(updated)
    assert [(item["id"], item["name"]["en"]) for item in documents] == [
        ("bank-details", "Bank details"), ("identity", "Updated identity proof"), ("residence", "Residence proof"),
    ]
    assert aliases == {"0": "bank-details", "ops:Identity proof": "identity"}
    assert section_statuses(updated)["required_documents"] == "official_source_unspecified"
    assert section_statuses({})["required_documents"] == "verification_pending"
