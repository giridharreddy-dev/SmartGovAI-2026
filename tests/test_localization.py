"""Automated regression tests for global Telugu ↔ English localization system."""

import json
from pathlib import Path
import pytest
from app import app, load_schemes, catalog_chat_fallback
from services.chat_service import retrieve_relevant_schemes, _build_scheme_context


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_all_schemes_have_complete_bilingual_descriptions():
    """Verify all 36 schemes in the catalog have non-empty telugu_description and english_description."""
    schemes = load_schemes()
    assert len(schemes) == 36, f"Expected 36 schemes, found {len(schemes)}"

    for name, data in schemes.items():
        # Telugu description
        telugu_desc = data.get("telugu_description") or data.get("telugu", {}).get("description")
        assert telugu_desc, f"Scheme {name} missing telugu_description"
        assert len(telugu_desc.strip()) > 30, f"Scheme {name} telugu_description is too short: {telugu_desc}"

        # English description
        english_desc = data.get("english_description") or data.get("simplified", {}).get("description")
        assert english_desc, f"Scheme {name} missing english_description"
        assert len(english_desc.strip()) > 30, f"Scheme {name} english_description is too short: {english_desc}"

        # Level and Category
        assert data.get("level") in ("Andhra Pradesh", "National"), f"Scheme {name} invalid level: {data.get('level')}"
        assert data.get("category"), f"Scheme {name} missing category"


def test_index_page_has_global_language_toggle(client):
    """Verify index.html contains the global header language switcher and Telugu default."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # HTML lang attribute
    assert '<html lang="te">' in html

    # Header language toggle group and buttons
    assert 'id="langTeBtn"' in html
    assert 'id="langEnBtn"' in html
    assert 'class="lang-toggle-group"' in html

    # Telugu is active by default
    assert 'id="langTeBtn" class="lang-btn active"' in html

    # i18n script is loaded
    assert 'i18n.js' in html


def test_no_per_scheme_english_details_button(client):
    """Verify that individual scheme cards do NOT have 'English Details' collapsible sections."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Ensure removed English Details collapsible tag does not exist
    assert "English Details" not in html
    assert "<summary>English Details</summary>" not in html


def test_chat_service_bilingual_retrieval():
    """Verify RAG retrieval and context generation in both Telugu and English modes."""
    schemes = load_schemes()

    # Telugu query
    te_matches = retrieve_relevant_schemes("ఆరోగ్యశ్రీ ఆసుపత్రి ఉచిత చికిత్స", schemes, lang="te")
    assert len(te_matches) > 0
    top_name = te_matches[0]["scheme_name"]
    te_context = _build_scheme_context(top_name, schemes[top_name], lang="te")
    assert te_context["scheme_name"]
    assert te_context["description"]
    assert "వైద్య" in te_context["description"] or "ఆరోగ్య" in te_context["description"] or "ఆసుపత్రి" in te_context["description"]

    # English query
    en_matches = retrieve_relevant_schemes("Aarogyasri hospital free treatment", schemes, lang="en")
    assert len(en_matches) > 0
    top_en_name = en_matches[0]["scheme_name"]
    en_context = _build_scheme_context(top_en_name, schemes[top_en_name], lang="en")
    assert en_context["scheme_name"]
    assert en_context["description"]
    assert "health" in en_context["description"].lower() or "treatment" in en_context["description"].lower() or "hospital" in en_context["description"].lower()


def test_chat_endpoint_language_support(client):
    """Verify /chat endpoint returns localized fallback when Gemini is unavailable."""
    schemes = load_schemes()
    matched = retrieve_relevant_schemes("Aarogyasri", schemes, lang="en")

    # English fallback
    en_fallback = catalog_chat_fallback(matched, lang="en")
    assert "Here are the relevant health schemes" in en_fallback
    assert "Please verify final eligibility" in en_fallback

    # Telugu fallback
    te_fallback = catalog_chat_fallback(matched, lang="te")
    assert "మీ ప్రశ్నకు సరిపోయే పథకాలు ఇవి:" in te_fallback
    assert "చివరి అర్హత కోసం" in te_fallback

    # Post to /chat in Telugu
    te_resp = client.post("/chat", json={"question": "ఆరోగ్యశ్రీ అంటే ఏమిటి?", "lang": "te"})
    assert te_resp.status_code == 200
    te_json = te_resp.get_json()
    assert "answer" in te_json
    assert len(te_json["matched_schemes"]) > 0

    # Post to /chat in English
    en_resp = client.post("/chat", json={"question": "What is Aarogyasri?", "lang": "en"})
    assert en_resp.status_code == 200
    en_json = en_resp.get_json()
    assert "answer" in en_json
    assert len(en_json["matched_schemes"]) > 0


def test_i18n_dictionary_completeness():
    """Verify i18n dictionary file exists and contains all required UI keys."""
    i18n_path = Path(__file__).resolve().parent.parent / "static" / "i18n.js"
    assert i18n_path.exists()
    content = i18n_path.read_text(encoding="utf-8")

    # Essential UI keys must be defined in the dictionary
    required_keys = [
        "appTitle",
        "langToggleTe",
        "langToggleEn",
        "searchPlaceholder",
        "filterAll",
        "filterAp",
        "filterNational",
        "symptomTitle",
        "chatTitle",
        "quizTitle",
        "docChecklistTitle",
        "guidedStep",
        "guidedTitle1",
        "speakPageBtn",
        "startGuidedModeBtn",
        "shareResultBtn",
        "printChecklistBtn",
    ]

    for key in required_keys:
        assert f"{key}:" in content, f"i18n.js missing key {key}"


def test_i18n_microphone_errors_and_staff_tools_keys():
    """Verify i18n dictionary contains keys for mic errors, staff tools, feedback status, and map controls."""
    i18n_path = Path(__file__).resolve().parent.parent / "static" / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    expected_keys = [
        "voiceErrNotAllowed",
        "voiceErrNoSpeech",
        "voiceErrAudioCapture",
        "voiceErrNetwork",
        "voiceErrAborted",
        "voiceErrGeneric",
        "voiceNotSupported",
        "voiceStartError",
        "voiceBtnTitle",
        "selectSchemeFromList",
        "selectDropdownPlaceholder",
        "showDetailsBtn",
        "pdfDocumentLabel",
        "feedbackSuccess",
        "feedbackError",
        "feedbackSaving",
        "networkError",
        "mapSelectDistrict",
        "mapSelectMandal",
        "mapSelectVillage",
        "mapLocationFinding",
        "mapLocationBtn",
        "mapErrDenied",
        "mapErrUnavailable",
        "mapErrTimeout",
        "mapErrNotFound",
        "mapYourLocationPopup",
        "mapFoundCount",
    ]
    for key in expected_keys:
        assert f"{key}:" in content, f"i18n.js missing key {key}"


def test_i18n_helper_functions_defined():
    """Verify i18n.js exposes required helper functions for scheme names, subtitles, descriptions, and mic errors."""
    i18n_path = Path(__file__).resolve().parent.parent / "static" / "i18n.js"
    content = i18n_path.read_text(encoding="utf-8")

    assert "getLocalizedSchemeName" in content
    assert "getLocalizedSchemeSubtitle" in content
    assert "getLocalizedSchemeDescription" in content
    assert "getLocalizedMicError" in content
    assert "translateCategory" in content
    assert "translateLevel" in content


def test_template_staff_tools_and_voice_elements(client):
    """Verify templates/index.html includes all i18n attributes for staff tools and voice controls."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Staff tools i18n markup
    assert 'data-i18n="staffToolsSummary"' in html
    assert 'data-i18n="selectSchemeFromList"' in html
    assert 'data-i18n="showDetailsBtn"' in html
    assert 'data-i18n="pdfDocumentLabel"' in html
    assert 'data-i18n="pdfSimplifyBtn"' in html

    # Voice search status element
    assert 'id="voiceStatus"' in html
    assert 'id="voiceBtn"' in html
    assert 'id="schemeSelect"' in html

