import sqlite3
from contextlib import closing
from xml.etree import ElementTree

from scripts.discover_schemes import catalog_keys, draft_entries, pib_leads, queue
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
            ("pib:1", "New training scheme", "", "https://pib.gov.in/?PRID=1",
             "https://pib.gov.in/rss", "PIB", "https://pib.gov.in/policy", "2026-11-05"),
        )
    _, replay = pib_leads(feed(("New training scheme", "https://pib.gov.in/?PRID=1", None)), {})
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
