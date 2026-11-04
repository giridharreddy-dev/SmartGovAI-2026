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
from datetime import UTC, date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen
from xml.etree import ElementTree

from scripts.extract_scheme_operations import extract_operations
from scripts.pib_excerpt import release_excerpts, release_id
from scripts.pib_regional import MATCH_RULE, find_regional_release, read_regional_index, same_event
from scripts.pib_translate import DEFAULT_MODEL_DIR, MODEL, REVISION, LocalTranslator
from services.scheme_operations import OperationalDraft, SchemeOperations, Text
from services.studio_catalog import load_studio_schemes
from utils import generate_slug

ROOT = Path(__file__).resolve().parents[1]
PIB_FEED = "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3&reg=48"
PIB_POLICY = "https://www.pib.gov.in/content/3622_2_CopyrightPolicy.aspx?lang=6&reg=17"
PIB_HOSTS = {"pib.gov.in", "www.pib.gov.in"}
SCHEME_WORDS = re.compile(r"\b(schemes?|yojana|abhiyan|scholarships?|pensions?|subsid(?:y|ies)|pmssy)\b", re.I)
BROAD_RELEASE = re.compile(
    r"\b(?:budget allocations?|budget outlays?|multi ministry|across ministries|"
    r"(?:multiple|several|various) (?:\w+ ){0,3}(?:schemes|ministries)|"
    r"(?:schemes|allocations) across)\b"
)
EXPLICIT_ALIASES = {
    "PM Surya Ghar: Muft Bijli Yojana": ("PM Surya Ghar", "సూర్య ఘర్ ముఫ్త్ బిజ్‌లీ యోజన"),
    "Ayushman Bharat PM-JAY (National Health Cover)": ("PM-JAY", "PMJAY"),
    "Ayushman Arogya Mandir (Free Primary Health Care)": ("AB-HWC", "AB-HWCs"),
}
AYUSHMAN_COMPONENTS = {
    "Ayushman Bharat PM-JAY (National Health Cover)",
    "Ayushman Arogya Mandir (Free Primary Health Care)",
}
MAX_FEED_BYTES = 1_000_000
TRANSLATION_GRACE = timedelta(hours=6)


def utc_now():
    return datetime.now(UTC)


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
    candidate_ids: tuple[str, ...] = ()


def normalized(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    text = text.replace("\u200c", "").replace("\u200d", "")
    return " ".join("".join(char if unicodedata.category(char)[0] in "LMN" else " " for char in text).split())


def https_url(value):
    parts = urlsplit(value)
    return parts.scheme == "https" and parts.hostname and not parts.username and not parts.password


def source_catalog():
    legacy = json.loads((ROOT / "data" / "merged_schemes.json").read_text(encoding="utf-8"))
    return {**load_studio_schemes(ROOT), **legacy}


def catalog_keys(schemes=None):
    schemes = source_catalog() if schemes is None else schemes
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
            *EXPLICIT_ALIASES.get(name, ()),
        ]
        candidates.append(slug)
        for candidate in candidates:
            alias = normalized(candidate)
            if len(alias.replace(" ", "")) >= 5 or re.fullmatch(r"[A-Z0-9-]{4,}", candidate):
                aliases.setdefault(alias, set()).add(slug)
        if name in AYUSHMAN_COMPONENTS:
            aliases.setdefault("ayushman bharat", set()).add(slug)
    return names, aliases


def match_catalog(title, aliases):
    text = normalized(title)
    mentions = [
        (hit.start(), hit.end(), alias)
        for alias in aliases
        for hit in re.finditer(rf"(?<!\S){re.escape(alias)}(?!\S)", text)
    ]
    # Suppress a nested alias only at the same occurrence, such as the umbrella
    # inside “Ayushman Bharat PM-JAY”. A separate mention still counts.
    specific = [
        alias for start, end, alias in mentions
        if not any(left <= start and end <= right and (left, right) != (start, end)
                   for left, right, _ in mentions)
    ]
    ids = tuple(sorted({slug for alias in specific for slug in aliases[alias]}))
    if (len(ids) > 1 or "ayushman bharat" in specific or BROAD_RELEASE.search(text)
            or (ids and re.search(r"\bpmssy\b", text) and "pmssy" not in aliases)):
        return "multi_scheme_lead", None, ids
    if ids:
        return "revision_candidate", ids[0], ids
    return "new_scheme_candidate", None, ()


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
        prid = release_id(url)
        if not prid or not title:
            continue
        lead_type, matched, candidates = match_catalog(title, aliases)
        if lead_type == "new_scheme_candidate" and not SCHEME_WORDS.search(title):
            continue
        published = publication_date(item.findtext("pubDate"))
        canonical_url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}"
        fingerprint = hashlib.sha256(f"{canonical_url}\n{published or ''}".encode()).hexdigest()
        rows.append(Lead(
            id=f"pib:{fingerprint}", event_key=f"pib:{prid}", title=title, region="", url=url,
            source_url=PIB_FEED, publisher="Press Information Bureau", policy_url=PIB_POLICY,
            type=lead_type, matched_catalog_id=matched, published_on=published, candidate_ids=candidates,
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


def queue(database, rows, aliases=None):
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
            "candidate_ids": "TEXT",
            "article_evidence": "TEXT",
            "translation_ready_at_utc": "TEXT",
        }
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(f"ALTER TABLE scheme_leads ADD COLUMN {name} {definition}")
        connection.execute("UPDATE scheme_leads SET event_key = id WHERE event_key IS NULL")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS scheme_leads_event ON scheme_leads(event_key)")
        ready_at = (utc_now() + TRANSLATION_GRACE).isoformat(timespec="seconds")
        # Older queues stored only a calendar date. Give those leads a fresh
        # grace period instead of guessing their original intake time.
        connection.execute(
            """UPDATE scheme_leads SET translation_ready_at_utc = ?
               WHERE translation_ready_at_utc IS NULL AND event_key LIKE 'pib:%'""",
            (ready_at,),
        )
        if aliases is not None:
            legacy = connection.execute(
                """SELECT id, title FROM scheme_leads WHERE candidate_ids IS NULL
                   AND event_key LIKE 'pib:%' AND status = 'pending_verification'"""
            ).fetchall()
            for lead in legacy:
                lead_type, matched, candidates = match_catalog(lead["title"], aliases)
                connection.execute(
                    "UPDATE scheme_leads SET type = ?, matched_catalog_id = ?, candidate_ids = ? WHERE id = ?",
                    (lead_type, matched, json.dumps(candidates), lead["id"]),
                )
        today = date.today().isoformat()
        values = [
            dict(asdict(row), discovered_on=today, candidate_ids=json.dumps(row.candidate_ids),
                 translation_ready_at_utc=ready_at if row.event_key.startswith("pib:") else None)
            for row in rows
        ]
        added = connection.executemany(
            """INSERT OR IGNORE INTO scheme_leads
                (id, title, region, url, source_url, publisher, policy_url, discovered_on,
                 event_key, type, matched_catalog_id, published_on, status, candidate_ids, translation_ready_at_utc)
                VALUES (:id, :title, :region, :url, :source_url, :publisher, :policy_url, :discovered_on,
                        :event_key, :type, :matched_catalog_id, :published_on, :status, :candidate_ids, :translation_ready_at_utc)""",
            values,
        ).rowcount
        # PIB releases may initially omit pubDate. A later date enriches the
        # same PRID rather than creating a second review item.
        connection.executemany(
            """UPDATE scheme_leads
               SET published_on = COALESCE(published_on, :published_on),
                   article_evidence = CASE WHEN title IS NOT :title THEN NULL ELSE article_evidence END,
                   title = :title,
                   type = :type,
                   matched_catalog_id = :matched_catalog_id,
                   candidate_ids = :candidate_ids
               WHERE event_key = :event_key AND status = 'pending_verification'
                 AND event_key LIKE 'pib:%'
                 AND ((published_on IS NULL AND :published_on IS NOT NULL)
                   OR title IS NOT :title OR type IS NOT :type OR matched_catalog_id IS NOT :matched_catalog_id
                   OR candidate_ids IS NOT :candidate_ids)""",
            values,
        )
        report = [dict(row) for row in connection.execute("SELECT * FROM scheme_leads ORDER BY discovered_on DESC, id")]
    for lead in report:
        lead["candidate_ids"] = json.loads(lead["candidate_ids"] or "[]")
        lead["article_evidence"] = json.loads(lead["article_evidence"]) if lead["article_evidence"] else None
    return added, report


def save_article_evidence(database, lead, updates):
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT article_evidence FROM scheme_leads WHERE id = ? AND title = ? AND status = 'pending_verification'",
            (lead["id"], lead["title"]),
        ).fetchone()
        if not row:
            return
        article = json.loads(row[0]) if row[0] else {}
        if "auto_te" in updates and article.get("te"):
            return
        official = updates.get("te")
        if official and official.get("match_method") == "regional_feed":
            prid = release_id(official["url"])
            claimed = connection.execute(
                """SELECT 1 FROM scheme_leads WHERE id <> ?
                   AND (json_extract(article_evidence, '$.te.release_id') = ?
                     OR json_extract(article_evidence, '$.te.url') = ?) LIMIT 1""",
                (lead["id"], prid, official["url"]),
            ).fetchone()
            if claimed:
                return
            updates = dict(updates, te=dict(official, release_id=prid))
        reconciled = bool(official and not article.get("te") and article.get("auto_te"))
        if reconciled:
            previous = article.pop("auto_te")
            article["reconciliation"] = {
                "replaces_auto_draft": True,
                "official_release_url": official["url"],
                "reconciled_at_utc": utc_now().isoformat(timespec="seconds"),
                "previous_model": previous["model"],
            }
        article.update(updates)
        connection.execute(
            "UPDATE scheme_leads SET article_evidence = ? WHERE id = ?",
            (json.dumps(article, ensure_ascii=False), lead["id"]),
        )
    if reconciled:
        print(f"Reconciled Telugu draft for {lead['event_key']} with {official['url']}.")
    lead["article_evidence"] = article


def enrich_drafts(database, leads, aliases, limit):
    pending = [
        lead for lead in leads if lead["status"] == "pending_verification"
        and lead["event_key"].startswith("pib:")
    ]
    uncached = [lead for lead in pending if not (lead["article_evidence"] or {}).get("en", {}).get("article_body_text")]
    for lead in uncached[:limit]:
        try:
            article = release_excerpts(lead["event_key"].removeprefix("pib:"))
        except (OSError, ValueError) as error:
            print(f"Could not read PIB release {lead['event_key']}: {type(error).__name__}")
            continue
        if article:
            save_article_evidence(database, lead, article)

    needs_te = [lead for lead in pending if lead["article_evidence"]
                and lead["article_evidence"].get("en") and not lead["article_evidence"].get("te")]
    if not needs_te:
        return
    try:
        regional = read_regional_index(database)
    except (OSError, ValueError, ElementTree.ParseError) as error:
        print(f"Could not index PIB Telugu RSS: {type(error).__name__}")
        return
    indexed = [(match_catalog(title, aliases)[1], url) for title, url in regional]
    for lead in needs_te[:limit]:
        if not lead["matched_catalog_id"]:
            continue
        urls = [url for scheme_id, url in indexed if scheme_id == lead["matched_catalog_id"]]
        if not urls:
            continue
        signature = hashlib.sha256("\n".join([MATCH_RULE, *sorted(urls)]).encode()).hexdigest()
        if lead["article_evidence"].get("regional_checked") == signature:
            continue
        try:
            regional_article = find_regional_release(lead["article_evidence"]["en"], urls)
        except (OSError, ValueError) as error:
            print(f"Could not compare Telugu PIB release for {lead['event_key']}: {type(error).__name__}")
            continue
        updates = {"regional_checked": signature}
        if regional_article:
            other_matches = [
                other for other in leads if other["id"] != lead["id"]
                and other["matched_catalog_id"] == lead["matched_catalog_id"]
                and same_event((other["article_evidence"] or {}).get("en", {}), regional_article)
            ]
            if not other_matches:
                updates["te"] = regional_article
        save_article_evidence(database, lead, updates)


def translated_draft(article):
    english = article.get("en", {}).get("translation_source", "")
    source_hash = hashlib.sha256(english.encode()).hexdigest()
    draft = article.get("auto_te") or {}
    return draft if draft.get("source_hash") == source_hash and draft.get("revision") == REVISION else None


def waiting_for_telugu(lead, now):
    ready_at = lead.get("translation_ready_at_utc")
    return bool(ready_at and datetime.fromisoformat(ready_at) > now)


def translate_drafts(database, leads, evidence, model_dir, limit):
    pending = []
    now = utc_now()
    waiting = 0
    for lead in leads:
        article = lead["article_evidence"] or {}
        manual = evidence.get(lead["id"], {})
        has_telugu = isinstance(manual, dict) and isinstance(manual.get("te"), dict) and manual["te"].get("summary")
        if (lead["status"] == "pending_verification" and article.get("en", {}).get("translation_source")
                and not (has_telugu or article.get("te") or translated_draft(article))):
            if waiting_for_telugu(lead, now):
                waiting += 1
            else:
                pending.append(lead)
    if waiting:
        print(f"Waiting for a Telugu release before translating {waiting} lead(s).")
    if not pending:
        return
    try:
        translator = LocalTranslator(model_dir)
    except (ImportError, OSError, ValueError, RuntimeError) as error:
        print(f"Local Telugu translation unavailable: {error}")
        return
    for lead in pending[:limit]:
        english = lead["article_evidence"]["en"]["translation_source"]
        try:
            summary = translator.translate(english)
        except (OSError, ValueError, RuntimeError) as error:
            print(f"Could not translate {lead['event_key']}: {error}")
            continue
        save_article_evidence(database, lead, {"auto_te": {
            "summary": summary, "model": MODEL, "revision": REVISION,
            "source_hash": hashlib.sha256(english.encode()).hexdigest(),
            "source_url": lead["article_evidence"]["en"]["url"],
        }})


def excerpt_metadata(article):
    if article is None:
        return None
    return {
        language: {key: value for key, value in article[language].items()
                   if key not in {"article_body_text", "translation_source"}}
        for language in ("en", "te") if language in article
    }


def draft_entries(leads, evidence, catalog_titles=None):
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
            "candidate_ids": lead["candidate_ids"],
            "status": "pending_verification",
            "lead_title": lead["title"],
            "announcement_url": lead["url"],
            "official_url": official_url,
            "category": source.get("category"),
            "article_evidence": excerpt_metadata(lead["article_evidence"]),
        }
        for language in ("en", "te"):
            fields = source.get(language, {})
            if not isinstance(fields, dict):
                raise ValueError(f"Invalid {language} draft evidence for {lead['id']}.")
            draft[language] = {}
            for key in ("summary", "eligibility"):
                value = fields.get(key)
                draft[language][key] = (value.strip() or None) if isinstance(value, str) else None
            article = (lead["article_evidence"] or {}).get(language)
            if article and draft[language]["summary"] is None:
                draft[language]["summary"] = article["excerpt"]
        automatic = translated_draft(lead["article_evidence"] or {})
        if automatic and not draft["te"]["summary"]:
            summary = re.sub(r"\s+([,.!?:;)])", r"\1", automatic["summary"])
            summary = summary.replace("( ", "(")
            draft["te"].update(
                summary="[AUTO-DRAFT] " + summary,
                status="pending_human_verification",
                model=automatic["model"],
                source_url=automatic["source_url"],
            )
        reconciliation = (lead["article_evidence"] or {}).get("reconciliation")
        if reconciliation:
            draft["reconciliation"] = reconciliation
        if not draft["te"]["summary"] and waiting_for_telugu(lead, utc_now()):
            draft["translation_ready_at_utc"] = lead["translation_ready_at_utc"]
        operations, passages = extract_operations(lead["article_evidence"] or {})
        if "operations" in source:
            operations = SchemeOperations.model_validate(source["operations"])
        title = (catalog_titles or {}).get(lead["matched_catalog_id"])
        structured = OperationalDraft(
            id=lead["matched_catalog_id"] or lead["id"],
            title=Text.model_validate(source.get("title", title or {"en": lead["title"]})),
            operational_status="pending_human_verification",
            **operations.model_dump(mode="json"),
        )
        title_source = "evidence" if "title" in source else "catalog" if title else "announcement_headline"
        draft.update(structured.model_dump(mode="json"), operational_evidence=passages, title_source=title_source)
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
    mode.add_argument("--queued-only", action="store_true", help="Work from the existing queue without fetching the English discovery feed")
    parser.add_argument("--source-url", help="Official dataset page, required for CSV")
    parser.add_argument("--publisher", help="Dataset publisher, required for CSV")
    parser.add_argument("--license-url", help="Dataset reuse terms, required for CSV")
    parser.add_argument("--database", type=Path, default=ROOT / "scratch" / "scheme-leads.db")
    parser.add_argument("--report", type=Path, help="Optional JSON review queue export")
    parser.add_argument("--drafts", type=Path, help="Optional pending bilingual draft export")
    parser.add_argument("--fetch-excerpts", action="store_true", help="With --drafts, fetch up to five uncached PIB releases")
    parser.add_argument("--translate-telugu", action="store_true", help="With --drafts, translate missing Telugu summaries locally")
    parser.add_argument("--translation-model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--evidence", type=Path, help="JSON keyed by lead ID with official_url and optional bilingual title, summaries and four-block operations")
    args = parser.parse_args()
    if args.csv and not (https_url(args.source_url or "") and args.publisher and https_url(args.license_url or "")):
        parser.error("--csv requires --source-url, --publisher and --license-url")
    if args.evidence and not args.drafts:
        parser.error("--evidence requires --drafts")
    if args.fetch_excerpts and not args.drafts:
        parser.error("--fetch-excerpts requires --drafts")
    if args.translate_telugu and not args.drafts:
        parser.error("--translate-telugu requires --drafts")
    try:
        paths = [path.resolve() for path in (args.database, args.report, args.drafts, args.evidence, args.csv) if path]
        if len(set(paths)) != len(paths):
            raise ValueError("Use different paths for the database, exports, and inputs.")
        if args.report:
            check_export(args.report, "leads")
        if args.drafts:
            check_export(args.drafts, "drafts")
        evidence = json.loads(args.evidence.read_text(encoding="utf-8-sig")) if args.evidence else {}
        if not isinstance(evidence, dict):
            raise ValueError("Draft evidence must be a JSON object keyed by lead ID.")
        catalog = source_catalog()
        names, aliases = catalog_keys(catalog)
        if args.queued_only:
            scanned, rows = 0, []
        else:
            if args.csv:
                scanned, rows = read_csv(args.csv, args.source_url, args.publisher, args.license_url, names)
            else:
                scanned, rows = read_pib(aliases)
        added, report = queue(args.database, rows, aliases)
        if args.fetch_excerpts:
            enrich_drafts(args.database, report, aliases, limit=5)
        if args.translate_telugu:
            translate_drafts(args.database, report, evidence, args.translation_model_dir, limit=5)
        titles = {
            scheme.get("slug") or generate_slug(name): {"en": name, "te": scheme.get("telugu_name") or None}
            for name, scheme in catalog.items()
        } if args.drafts else {}
        drafts = draft_entries(report, evidence, titles) if args.drafts else None
        if args.report:
            export_report(args.report, "leads", [
                dict(lead, article_evidence=excerpt_metadata(lead["article_evidence"])) for lead in report
            ])
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
