"""Index the independent PIB Telugu feed and shortlist localized releases."""

import re
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from urllib.parse import urlsplit
from urllib.request import urlopen
from xml.etree import ElementTree

from scripts.pib_excerpt import HOSTS, regional_article, release_id

TELUGU_FEED = "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=16&Regid=5&reg=5"
MINISTRY_ALIASES = {
    "ప్రధాన మంత్రి కార్యాలయం": "prime minister's office",
    "ప్రధానమంత్రి కార్యాలయం": "prime minister's office",
    "సాంఘిక న్యాయం మరియు సాధికారత మంత్రిత్వ శాఖ": "ministry of social justice and empowerment",
    "సామాజిక న్యాయం సాధికారత మంత్రిత్వ శాఖ": "ministry of social justice and empowerment",
    "ఆరోగ్య కుటుంబ సంక్షేమ మంత్రిత్వ శాఖ": "ministry of health and family welfare",
    "నూతన పునరుత్పాదక ఇంధన మంత్రిత్వ శాఖ": "ministry of new and renewable energy",
}
EXACT_TIME_WINDOW = timedelta(minutes=20)


def telugu_text(text):
    letters = [character for character in text if character.isalpha()]
    return bool(letters) and sum("\u0c00" <= character <= "\u0c7f" for character in letters) >= len(letters) * 0.65


def read_regional_index(database):
    with urlopen(TELUGU_FEED, timeout=10) as response:
        payload = response.read(1_000_001)
        if urlsplit(response.url).hostname not in HOSTS or len(payload) > 1_000_000:
            raise ValueError("PIB returned an unexpected regional feed.")
    if re.search(br"<!\s*(?:DOCTYPE|ENTITY)", payload, re.I):
        raise ValueError("PIB returned an unexpected XML declaration.")
    channel = ElementTree.fromstring(payload).find("./channel")
    if channel is None:
        raise ValueError("PIB did not return a regional RSS channel.")
    rows = []
    for item in channel.findall("item"):
        title = " ".join(item.findtext("title", "").split())
        url = item.findtext("link", "").strip()
        prid = release_id(url)
        if prid and telugu_text(title):
            rows.append((prid, title, url, date.today().isoformat()))
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS pib_telugu_index (
            prid TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, seen_on TEXT NOT NULL
        )""")
        connection.executemany(
            """INSERT INTO pib_telugu_index VALUES (?, ?, ?, ?)
               ON CONFLICT(prid) DO UPDATE SET title=excluded.title, url=excluded.url, seen_on=excluded.seen_on""",
            rows,
        )
        recent = (date.today() - timedelta(days=7)).isoformat()
        return connection.execute(
            "SELECT title, url FROM pib_telugu_index WHERE seen_on >= ? ORDER BY seen_on DESC, prid DESC",
            (recent,),
        ).fetchall()


def same_event(english, telugu):
    if not all(english.get(key) and telugu.get(key) for key in ("ministry", "posted_at_ist")):
        return False
    def ministry_key(value):
        return " ".join(value.casefold().replace("’", "'").replace("&", " and ")
                        .replace(",", " ").replace("\u200c", "").replace("\u200d", "").split())

    en_ministry = ministry_key(english["ministry"])
    te_ministry = ministry_key(telugu["ministry"])
    if en_ministry != MINISTRY_ALIASES.get(te_ministry, te_ministry):
        return False
    return abs(datetime.fromisoformat(english["posted_at_ist"]) - datetime.fromisoformat(telugu["posted_at_ist"])) <= EXACT_TIME_WINDOW


def find_regional_release(english, urls):
    # A shortlist that is too broad needs manual review. Never pick the first
    # release merely because it shares a ministry or timestamp.
    if not 0 < len(urls) <= 3:
        return None
    matches = []
    for url in urls:
        article = regional_article(url)
        if article and same_event(english, article):
            matches.append(article)
    return dict(matches[0], match_method="regional_feed") if len(matches) == 1 else None
