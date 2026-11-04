"""Collect scheme leads from PIB RSS or a licensed CSV into a local review queue."""

import argparse
import csv
import json
import re
import sqlite3
import tempfile
import unicodedata
from contextlib import closing
from datetime import date
from pathlib import Path
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen
from xml.etree import ElementTree

from services.studio_catalog import load_studio_schemes

ROOT = Path(__file__).resolve().parents[1]
PIB_FEED = "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3&reg=48"
PIB_POLICY = "https://www.pib.gov.in/content/3622_2_CopyrightPolicy.aspx?lang=6&reg=17"
PIB_HOSTS = {"pib.gov.in", "www.pib.gov.in"}
SCHEME_WORDS = re.compile(r"\b(schemes?|yojana|abhiyan|scholarships?|pensions?|subsid(?:y|ies))\b", re.I)
MAX_FEED_BYTES = 1_000_000


def normalized(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    return " ".join("".join(char if unicodedata.category(char)[0] in "LMN" else " " for char in text).split())


def https_url(value):
    parts = urlsplit(value)
    return parts.scheme == "https" and parts.hostname and not parts.username and not parts.password


def catalog_keys():
    legacy = json.loads((ROOT / "data" / "merged_schemes.json").read_text(encoding="utf-8"))
    schemes = {**load_studio_schemes(ROOT), **legacy}
    names, headline_names = set(), set()
    for name, scheme in schemes.items():
        title = normalized(name)
        region = normalized(scheme.get("level") or "National")
        names.add((title, region))
        headline_names.add(title)
        slug = scheme.get("slug", "")
        if slug.startswith("welfare-"):
            headline_names.add(normalized(slug.removeprefix("welfare-")))
    return names, {title for title in headline_names if len(title) >= 8 and " " in title}


def pib_leads(payload, headline_names):
    if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
        raise ValueError("PIB returned an unexpected XML declaration.")
    channel = ElementTree.fromstring(payload).find("./channel")
    if channel is None:
        raise ValueError("PIB did not return an RSS channel.")
    rows = []
    items = channel.findall("item")
    for item in items:
        title = " ".join(item.findtext("title", "").split())
        url = item.findtext("link", "").strip()
        parts = urlsplit(url)
        prid = parse_qs(parts.query).get("PRID", [""])[0]
        if not https_url(url) or parts.hostname not in PIB_HOSTS or not prid.isdecimal():
            continue
        if not SCHEME_WORDS.search(title):
            continue
        phrase = f" {normalized(title)} "
        if any(f" {name} " in phrase for name in headline_names):
            continue
        rows.append((f"pib:{prid}", title, "", url, PIB_FEED, "Press Information Bureau", PIB_POLICY))
    return len(items), rows


def read_pib(headline_names):
    with urlopen(PIB_FEED, timeout=15) as response:
        if urlsplit(response.url).hostname not in PIB_HOSTS:
            raise ValueError("The PIB feed redirected outside pib.gov.in.")
        payload = response.read(MAX_FEED_BYTES + 1)
    if len(payload) > MAX_FEED_BYTES:
        raise ValueError("The PIB feed exceeded its expected size.")
    return pib_leads(payload, headline_names)


def read_csv(path, source_url, publisher, license_url, known_names):
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if "name" not in (reader.fieldnames or []):
            raise ValueError("CSV requires a name column. The region and url columns are optional.")
        rows, count = [], 0
        for count, row in enumerate(reader, 1):
            name = " ".join((row.get("name") or "").split())
            region = " ".join((row.get("region") or "National").split())
            url = (row.get("url") or source_url).strip()
            key = (normalized(name), normalized(region))
            if not key[0] or key in known_names:
                continue
            if not https_url(url):
                raise ValueError(f"CSV record {count} has an invalid HTTPS URL.")
            rows.append(("csv:" + "|".join(key), name, region, url, source_url, publisher, license_url))
    return count, rows


def queue(database, rows):
    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.row_factory = sqlite3.Row
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scheme_leads (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, region TEXT NOT NULL,
                url TEXT NOT NULL, source_url TEXT NOT NULL, publisher TEXT NOT NULL,
                policy_url TEXT NOT NULL, discovered_on TEXT NOT NULL
            )
        """)
        before = connection.total_changes
        today = date.today().isoformat()
        connection.executemany(
            "INSERT OR IGNORE INTO scheme_leads VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(*row, today) for row in rows],
        )
        added = connection.total_changes - before
        report = [dict(row) for row in connection.execute("SELECT * FROM scheme_leads ORDER BY discovered_on DESC, id")]
    return added, report


def export_report(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode="w", encoding="utf-8") as output:
            temporary = Path(output.name)
            json.dump({"review_required": True, "leads": rows}, output, ensure_ascii=False, indent=2)
            output.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, help="Licensed UTF-8 CSV with name and optional region,url columns")
    parser.add_argument("--source-url", help="Official dataset page, required for CSV")
    parser.add_argument("--publisher", help="Dataset publisher, required for CSV")
    parser.add_argument("--license-url", help="Dataset reuse terms, required for CSV")
    parser.add_argument("--database", type=Path, default=ROOT / "scratch" / "scheme-leads.db")
    parser.add_argument("--report", type=Path, help="Optional JSON review queue export")
    args = parser.parse_args()
    if args.csv and not (https_url(args.source_url or "") and args.publisher and https_url(args.license_url or "")):
        parser.error("--csv requires --source-url, --publisher and --license-url")
    try:
        if args.report:
            if args.report.resolve() == args.database.resolve():
                raise ValueError("The report and database must use different paths.")
            previous = json.loads(args.report.read_text(encoding="utf-8")) if args.report.exists() else {}
            if (args.report.suffix.lower() != ".json" or args.report.exists()
                    and (not isinstance(previous, dict) or previous.get("review_required") is not True)):
                raise ValueError("--report must be a new JSON file or an existing review export.")
        names, headline_names = catalog_keys()
        if args.csv:
            scanned, rows = read_csv(args.csv, args.source_url, args.publisher, args.license_url, names)
        else:
            scanned, rows = read_pib(headline_names)
        added, report = queue(args.database, rows)
        if args.report:
            export_report(args.report, report)
    except (OSError, URLError, ValueError, ElementTree.ParseError, sqlite3.Error) as error:
        parser.exit(1, f"Discovery failed: {error}\n")
    print(f"Scanned {scanned}; added {added}; already queued {len(rows) - added}; filtered {scanned - len(rows)}.")
    print(f"Review queue: {len(report)} lead(s).")


if __name__ == "__main__":
    main()
