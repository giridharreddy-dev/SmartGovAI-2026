import sqlite3
from contextlib import closing
from hashlib import sha256
from unittest.mock import patch
from xml.etree import ElementTree

from scripts.discover_schemes import catalog_keys, draft_entries, match_catalog, pib_leads, queue, translated_draft
from scripts.pib_excerpt import parse_article, parse_release, release_id
from scripts.pib_regional import find_regional_release, same_event
from scripts.pib_translate import MODEL, REVISION, _telugu_script
from utils import generate_slug


def feed(*items):
    root = ElementTree.Element("rss")
    channel = ElementTree.SubElement(root, "channel")
    for title, url, date in items:
        item = ElementTree.SubElement(channel, "item")
        ElementTree.SubElement(item, "title").text = title
        ElementTree.SubElement(item, "link").text = url
        if date:
            ElementTree.SubElement(item, "pubDate").text = date
    return ElementTree.tostring(root, encoding="utf-8")


def test_known_scheme_releases_are_queued_and_deduplicated_by_release(tmp_path):
    _, aliases = catalog_keys()
    title = "Cabinet approves revision of income ceiling under Ayushman Bharat PM-JAY"
    first = "https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1"
    second = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2"
    date = "Thu, 05 Nov 2026 12:00:00 +0530"
    _, leads = pib_leads(feed((title, first, None), (title, second, date)), aliases)
    assert len(leads) == 2
    assert leads[0].id != leads[1].id
    assert all(lead.type == "revision_candidate" for lead in leads)
    assert all(lead.matched_catalog_id == generate_slug("Ayushman Bharat PM-JAY (National Health Cover)") for lead in leads)
    database = tmp_path / "leads.db"
    assert queue(database, leads)[0] == 2

    variant = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=1&lang=1"
    _, replay = pib_leads(feed((title, variant, date)), aliases)
    added, report = queue(database, replay)
    assert added == 0
    assert len(report) == 2
    by_event = {row["event_key"]: row for row in report}
    assert by_event["pib:1"]["id"] == leads[0].id
    assert by_event["pib:1"]["published_on"] == "2026-11-05"


def test_existing_queue_migrates_and_exports_only_pending_evidence(tmp_path):
    database = tmp_path / "leads.db"
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("""
            CREATE TABLE scheme_leads (
                id TEXT PRIMARY KEY, title TEXT, region TEXT, url TEXT,
                source_url TEXT, publisher TEXT, policy_url TEXT, discovered_on TEXT
            )
        """)
        connection.execute(
            "INSERT INTO scheme_leads VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("pib:1", "New training scheme", "", "https://pib.gov.in/PressReleasePage.aspx?PRID=1",
             "https://pib.gov.in/rss", "PIB", "https://pib.gov.in/policy", "2026-11-05"),
        )
    _, replay = pib_leads(feed(("New training scheme", "https://pib.gov.in/PressReleasePage.aspx?PRID=1", None)), {})
    added, report = queue(database, replay)
    assert added == 0
    assert report[0]["id"] == "pib:1"
    assert report[0]["type"] == "new_scheme_candidate"
    assert draft_entries(report, {})[0]["te"] == {"summary": None, "eligibility": None}
    evidence = {"pib:1": {"official_url": "https://example.org/guidelines", "te": {"summary": "శిక్షణ"}}}
    draft = draft_entries(report, evidence)[0]
    assert draft["status"] == "pending_verification"
    assert draft["te"] == {"summary": "శిక్షణ", "eligibility": None}
    assert draft["en"] == {"summary": None, "eligibility": None}


def test_multi_scheme_and_budget_headlines_leave_the_primary_id_unset(tmp_path):
    _, aliases = catalog_keys()
    jay = generate_slug("Ayushman Bharat PM-JAY (National Health Cover)")
    hwc = generate_slug("Ayushman Arogya Mandir (Free Primary Health Care)")
    assert match_catalog("Revised circular for PM-JAY", aliases) == ("revision_candidate", jay, (jay,))
    assert match_catalog("Cabinet statement on PM-JAY and AB-HWCs", aliases) == (
        "multi_scheme_lead", None, tuple(sorted((jay, hwc))),
    )
    assert match_catalog("New details under Ayushman Bharat", aliases) == (
        "multi_scheme_lead", None, tuple(sorted((jay, hwc))),
    )
    assert match_catalog("Cabinet approves health budget allocations", aliases) == ("multi_scheme_lead", None, ())
    assert match_catalog("Cabinet approves health budget allocations including PM-JAY", aliases) == (
        "multi_scheme_lead", None, (jay,),
    )
    assert match_catalog("PM attends a Surya Ghar event", aliases) == ("new_scheme_candidate", None, ())
    url = "https://pib.gov.in/PressReleasePage.aspx?PRID=1"
    database = tmp_path / "leads.db"
    _, first = pib_leads(feed(("Revised circular for PM-JAY", url, None)), aliases)
    assert queue(database, first)[1][0]["matched_catalog_id"] == jay
    broader = "Cabinet statement on PM-JAY and AB-HWCs"
    _, replay = pib_leads(feed((broader, url, None)), aliases)
    added, report = queue(database, replay)
    assert added == 0
    assert report[0]["title"] == broader
    assert report[0]["matched_catalog_id"] is None
    assert report[0]["candidate_ids"] == sorted((jay, hwc))


def test_pib_excerpt_comes_from_article_body_and_checks_language():
    url = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=12"
    english = "The department announced the programme guidelines and asked applicants to consult its official website."
    html = f"""
        <nav><p>The navigation contains many links that should never become the excerpt.</p></nav>
        <div id="pibReleaseBody"><p>{english}</p></div>
        <div class="ReleaseLang"><a href="/PressReleasePage.aspx?PRID=13">Telugu</a></div>
    """
    assert parse_release(html, url, "en") == (english, "https://www.pib.gov.in/PressReleasePage.aspx?PRID=13")
    assert parse_release(html, url, "te")[0] is None
    assert release_id("https://example.org/PressReleasePage.aspx?PRID=13") is None


def test_regional_pairing_requires_same_ministry_time_and_a_unique_candidate():
    english = {"ministry": "Prime Minister's Office", "posted_at_ist": "2026-11-04T20:54:00"}
    telugu = {"ministry": "ప్రధాన మంత్రి కార్యాలయం", "posted_at_ist": "2026-11-04T21:01:00"}
    assert same_event(english, telugu)
    assert not same_event(english, dict(telugu, posted_at_ist="2026-11-05T09:00:00"))
    assert not same_event(english, dict(telugu, ministry="Other ministry"))
    with patch("scripts.pib_regional.regional_article", return_value=telugu):
        assert find_regional_release(english, ["one"])["match_method"] == "regional_feed"
        assert find_regional_release(english, ["one", "two"]) is None


def test_article_body_stays_in_cache_and_machine_translation_is_tagged(tmp_path):
    url = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=12"
    full_text = "The department announced revised guidelines and asked applicants to review the official portal."
    html = f"""
        <div id="MinistryName">Prime Minister's Office</div>
        <div id="PrDateTime">Posted on: 04 NOV 2026 8:54 PM by PIB Delhi</div>
        <div id="pibReleaseBody"><p>{full_text}</p><p>Additional details here.</p></div>
    """
    article, _ = parse_article(html, url, "en")
    assert article["posted_at_ist"] == "2026-11-04T20:54:00"
    assert "Additional details here." in article["article_body_text"]
    assert _telugu_script("प्रभुत्वं पथकान्नि आमोदिंचिंदि।") == "ప్రభుత్వం పథకాన్ని ఆమోదించింది."
    translation = {"summary": "ప్రభుత్వం పథకాన్ని ఆమోదించింది.", "source_url": url,
                   "model": MODEL, "revision": REVISION,
                   "source_hash": sha256(article["translation_source"].encode()).hexdigest()}
    evidence = {"en": article, "auto_te": translation}
    assert translated_draft(evidence) == translation
    _, leads = pib_leads(feed(("Revised scheme details", url, None)), {})
    _, rows = queue(tmp_path / "leads.db", leads)
    rows[0]["article_evidence"] = evidence
    draft = draft_entries(rows, {})[0]
    assert draft["te"]["summary"].startswith("[AUTO-DRAFT] ")
    assert draft["te"]["status"] == "pending_human_verification"
    assert "article_body_text" not in draft["article_evidence"]["en"]
    assert draft["te"]["eligibility"] is None
    rows[0]["article_evidence"]["te"] = {"excerpt": "అధికారిక సమాచారం", "url": url}
    assert draft_entries(rows, {})[0]["te"]["summary"] == "అధికారిక సమాచారం"
