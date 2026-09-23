"""Template and stylesheet checks for high-priority citizen-facing interactions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_all_filter_is_not_preselected():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert 'class="filter-btn active" type="button" data-filter="all"' not in template
    assert 'class="filter-btn" type="button" data-filter="all"' in template


def test_scheme_details_always_scroll_into_view():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert "document.getElementById('resultArea').scrollIntoView" in template
    assert "prefers-reduced-motion: reduce" in template


def test_scheme_grid_renders_on_first_page_load():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert "let lastFilter = null;" in template


def test_scheme_lookup_uses_cached_data_when_offline():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

    assert "window.SmartGovEnhanced?.loadOfflineData()" in template
    assert "Cached SmartGovAI data" in template


def test_mobile_result_panel_follows_scheme_list():
    stylesheet = (ROOT / "static" / "style.css").read_text(encoding="utf-8")

    mobile_rules = stylesheet.split("@media (max-width: 1023px)", 1)[1].split("@media", 1)[0]
    assert "order: -1" not in mobile_rules


def test_chat_controls_have_client_handlers():
    script = (ROOT / "static" / "enhanced-features.js").read_text(encoding="utf-8")

    for action in ("open-chat", "close-chat", "chat-suggestion", "send-chat"):
        assert f"action === '{action}'" in script

def test_frontend_does_not_call_response_json_directly():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    
    # response.json() should only appear exactly once, safely guarded inside safeFetch
    occurrences = template.count("response.json()")
    assert occurrences == 1, f"Expected exactly one safe response.json() call, found {occurrences}"
    
    # Verify safeFetch is actually used by the main fetch paths
    assert "safeFetch(\"{{ url_for('simplify') }}\"" in template
    assert "safeFetch(\"{{ url_for('feedback') }}\"" in template


def test_chat_suggestions_have_localized_attributes():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'data-question-te="' in template
    assert 'data-question-en="' in template

def test_result_feedback_status_id_is_unique():
    template = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'id="resultFeedbackStatus"' in template
    assert 'id="feedbackStatus"' in template
    
    # Ensure they are distinct
    assert template.count('id="feedbackStatus"') == 1
    assert template.count('id="resultFeedbackStatus"') == 1
def test_speech_synthesis_language_selection():
    script = (ROOT / "static" / "enhanced-features.js").read_text(encoding="utf-8")
    assert "utterance.lang = isEn ? 'en-IN' : 'te-IN';" in script
    assert "utterance.voice = matchingVoice;" in script

