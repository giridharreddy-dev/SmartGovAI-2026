"""Collect scheme leads from PIB RSS or a licensed CSV into a local review queue."""

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import tempfile
import unicodedata
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen
from xml.etree import ElementTree

from services.studio_catalog import load_studio_schemes
from utils import generate_slug

ROOT = Path(__file__).resolve().parents[1]
PIB_FEED = "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3&reg=48"
PIB_POLICY = "https://www.pib.gov.in/content/3622_2_CopyrightPolicy.aspx?lang=6&reg=17"
PIB_HOSTS = {"pib.gov.in", "www.pib.gov.in"}
SCHEME_WORDS = re.compile(r"\b(schemes?|yojana|abhiyan|scholarships?|pensions?|subsid(?:y|ies))\b", re.I)
MAX_FEED_BYTES = 1_000_000


@dataclass(frozen=True)
class Lead:
    id: str
    title: str
    region: str
    url: str
    source_url: str
    publisher: str
    policy_url: str
    event_key: str
    type: str = "new_scheme_candidate"
    matched_catalog_id: str | None = None
    published_on: str | None = None
    status: str = "pending_verification"


def normalized(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    return " ".join("".join(char if unicodedata.category(char)[0] in "LMN" else " " for char in text).split())


def https_url(value):
    parts = urlsplit(value)
    return parts.scheme == "https" and parts.hostname and not parts.username and not parts.password


def catalog_keys():
    legacy = json.loads((ROOT / "data" / "merged_schemes.json").read_text(encoding="utf-8"))
    schemes = {**load_studio_schemes(ROOT), **legacy}
    names, aliases = set(), {}
    for name, scheme in schemes.items():
        region = normalized(scheme.get("level") or "National")
        names.add((normalized(name), region))
        slug = scheme.get("slug") or generate_slug(name)
        candidates = [
            name,
            re.sub(r"\s*\([^)]*\)", "", name),
            scheme.get("telugu_name") or "",
            *re.findall(r"\(([A-Z0-9-]{4,})\)", name),
        ]
        # Keep explicit acronym-like catalog keywords, excluding broad topic keywords.
        candidates.extend(
            word for word in (scheme.get("keywords") or [])
            if re.fullmatch(r"[A-Za-z]{2,}-[A-Za-z0-9]{2,}", word)
        )
        if slug.startswith("welfare-"):
            candidates.append(slug.removeprefix("welfare-"))
        for candidate in candidates:
            alias = normalized(candidate)
            if len(alias.replace(" ", "")) >= 4:
                aliases.setdefault(alias, set()).add(slug)
    return names, aliases


def match_catalog(title, aliases):
    phrase = f" {normalized(title)} "
    matches = [alias for alias in aliases if f" {alias} " in phrase]
    # Ignore a shorter alias contained in a more specific match. Keep a lead
    # unlinked when the remaining matches point to different schemes.
    specific = [alias for alias in matches
                if not any(alias != other and f" {alias} " in f" {other} " for other in matches)]
    ids = {slug for alias in specific for slug in aliases[alias]}
    return next(iter(ids)) if len(ids) == 1 else None, bool(ids)


def publication_date(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        try:
            return datetime.fromisoformat(value).date().isoformat()
        except ValueError:
            return None


def pib_leads(payload, aliases):
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
        parameters = {key.lower(): values for key, values in parse_qs(parts.query).items()}
        prid = parameters.get("prid", [""])[0]
        if not https_url(url) or parts.hostname not in PIB_HOSTS or not re.fullmatch(r"[0-9]+", prid):
            continue
        if not title:
            continue
        matched, mentions_catalog = match_catalog(title, aliases)
        if not mentions_catalog and not SCHEME_WORDS.search(title):
            continue
        published = publication_date(item.findtext("pubDate"))
        canonical_url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"
        fingerprint = hashlib.sha256(f"{canonical_url}\n{published or ''}".encode()).hexdigest()
        rows.append(Lead(
            id=f"pib:{fingerprint}", event_key=f"pib:{prid}", title=title, region="", url=url,
            source_url=PIB_FEED, publisher="Press Information Bureau", policy_url=PIB_POLICY,
            type="revision_candidate" if mentions_catalog else "new_scheme_candidate",
            matched_catalog_id=matched, published_on=published,
        ))
    return len(items), rows


def read_pib(aliases):
    with urlopen(PIB_FEED, timeout=15) as response:
        if urlsplit(response.url).hostname not in PIB_HOSTS:
            raise ValueError("The PIB feed redirected outside pib.gov.in.")
        payload = response.read(MAX_FEED_BYTES + 1)
    if len(payload) > MAX_FEED_BYTES:
        raise ValueError("The PIB feed exceeded its expected size.")
    return pib_leads(payload, aliases)


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
            identity = "csv:" + "|".join(key)
            rows.append(Lead(identity, name, region, url, source_url, publisher, license_url, identity))
    return count, rows


def queue(database, rows):
    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scheme_leads (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, region TEXT NOT NULL,
                url TEXT NOT NULL, source_url TEXT NOT NULL, publisher TEXT NOT NULL,
                policy_url TEXT NOT NULL, discovered_on TEXT NOT NULL
            )
        """)
        existing = {column["name"] for column in connection.execute("PRAGMA table_info(scheme_leads)")}
        additions = {
            "event_key": "TEXT",
            "type": "TEXT NOT NULL DEFAULT 'new_scheme_candidate'",
            "matched_catalog_id": "TEXT",
            "published_on": "TEXT",
            "status": "TEXT NOT NULL DEFAULT 'pending_verification'",
        }
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(f"ALTER TABLE scheme_leads ADD COLUMN {name} {definition}")
        connection.execute("UPDATE scheme_leads SET event_key = id WHERE event_key IS NULL")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS scheme_leads_event ON scheme_leads(event_key)")
        today = date.today().isoformat()
        values = [dict(asdict(row), discovered_on=today) for row in rows]
        added = connection.executemany(
            """INSERT OR IGNORE INTO scheme_leads
                (id, title, region, url, source_url, publisher, policy_url, discovered_on,
                 event_key, type, matched_catalog_id, published_on, status)
                VALUES (:id, :title, :region, :url, :source_url, :publisher, :policy_url, :discovered_on,
                        :event_key, :type, :matched_catalog_id, :published_on, :status)""",
            values,
        ).rowcount
        # PIB releases may initially omit pubDate. A later date enriches the
        # same PRID rather than creating a second review item.
        connection.executemany(
            """UPDATE scheme_leads
               SET published_on = COALESCE(published_on, :published_on),
                   type = CASE WHEN :type = 'revision_candidate' THEN :type ELSE type END,
                   matched_catalog_id = COALESCE(matched_catalog_id, :matched_catalog_id)
               WHERE event_key = :event_key AND status = 'pending_verification'
                 AND ((published_on IS NULL AND :published_on IS NOT NULL)
                   OR (:type = 'revision_candidate' AND type <> :type)
                   OR (matched_catalog_id IS NULL AND :matched_catalog_id IS NOT NULL))""",
            values,
        )
        report = [dict(row) for row in connection.execute("SELECT * FROM scheme_leads ORDER BY discovered_on DESC, id")]
    return added, report


def draft_entries(leads, evidence):
    if not isinstance(evidence, dict):
        raise ValueError("Draft evidence must be a JSON object keyed by lead ID.")
    drafts = []
    for lead in leads:
        if lead["status"] != "pending_verification":
            continue
        source = evidence.get(lead["id"], {})
        if not isinstance(source, dict):
            raise ValueError(f"Invalid draft evidence for {lead['id']}.")
        official_url = source.get("official_url")
        if source and (not isinstance(official_url, str) or not https_url(official_url)):
            raise ValueError(f"Draft evidence for {lead['id']} needs an official HTTPS source URL.")
        draft = {
            "lead_id": lead["id"],
            "type": lead["type"],
            "matched_catalog_id": lead["matched_catalog_id"],
            "status": "pending_verification",
            "lead_title": lead["title"],
            "announcement_url": lead["url"],
            "official_url": official_url,
            "category": source.get("category"),
        }
        for language in ("en", "te"):
            fields = source.get(language, {})
            if not isinstance(fields, dict):
                raise ValueError(f"Invalid {language} draft evidence for {lead['id']}.")
            draft[language] = {}
            for key in ("summary", "eligibility"):
                value = fields.get(key)
                draft[language][key] = (value.strip() or None) if isinstance(value, str) else None
        drafts.append(draft)
    return drafts


def check_export(path, kind):
    if path.suffix.lower() != ".json":
        raise ValueError(f"The {kind} export must use a .json file.")
    if path.exists():
        previous = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(previous, dict) or previous.get("review_required") is not True or kind not in previous:
            raise ValueError(f"The {kind} export must use a new file or an existing {kind} export.")


def export_report(path, kind, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode="w", encoding="utf-8") as output:
            temporary = Path(output.name)
            json.dump({"review_required": True, kind: rows}, output, ensure_ascii=False, indent=2)
            output.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--csv", type=Path, help="Licensed UTF-8 CSV with name and optional region,url columns")
    mode.add_argument("--queued-only", action="store_true", help="Export the existing queue without fetching the feed")
    parser.add_argument("--source-url", help="Official dataset page, required for CSV")
    parser.add_argument("--publisher", help="Dataset publisher, required for CSV")
    parser.add_argument("--license-url", help="Dataset reuse terms, required for CSV")
    parser.add_argument("--database", type=Path, default=ROOT / "scratch" / "scheme-leads.db")
    parser.add_argument("--report", type=Path, help="Optional JSON review queue export")
    parser.add_argument("--drafts", type=Path, help="Optional pending bilingual draft export")
    parser.add_argument("--evidence", type=Path, help="JSON keyed by lead ID with official_url, category, and en/te summary and eligibility")
    args = parser.parse_args()
    if args.csv and not (https_url(args.source_url or "") and args.publisher and https_url(args.license_url or "")):
        parser.error("--csv requires --source-url, --publisher and --license-url")
    if args.evidence and not args.drafts:
        parser.error("--evidence requires --drafts")
    try:
        paths = [path.resolve() for path in (args.database, args.report, args.drafts, args.evidence, args.csv) if path]
        if len(set(paths)) != len(paths):
            raise ValueError("Use different paths for the database, exports, and inputs.")
        if args.report:
            check_export(args.report, "leads")
        if args.drafts:
            check_export(args.drafts, "drafts")
        evidence = json.loads(args.evidence.read_text(encoding="utf-8-sig")) if args.evidence else {}
        if args.queued_only:
            scanned, rows = 0, []
        else:
            names, aliases = catalog_keys()
            if args.csv:
                scanned, rows = read_csv(args.csv, args.source_url, args.publisher, args.license_url, names)
            else:
                scanned, rows = read_pib(aliases)
        added, report = queue(args.database, rows)
        drafts = draft_entries(report, evidence) if args.drafts else None
        if args.report:
            export_report(args.report, "leads", report)
        if args.drafts:
            export_report(args.drafts, "drafts", drafts)
    except (OSError, URLError, ValueError, ElementTree.ParseError, sqlite3.Error) as error:
        parser.exit(1, f"Discovery failed: {error}\n")
    print(f"Scanned {scanned}; added {added}; already queued {len(rows) - added}; filtered {scanned - len(rows)}.")
    print(f"Review queue: {len(report)} lead(s).")
    if args.drafts:
        print(f"Draft export: {len(drafts)} pending verification.")


if __name__ == "__main__":
    main()
