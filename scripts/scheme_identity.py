"""Resolve scheme identities for offline catalog reconciliation."""

import re
import unicodedata
from urllib.parse import parse_qsl, urlsplit

STOP_WORDS = frozenset("and of for the dr ysr pm pradhan mantri scheme yojana national ap programme program".split())
DISTINCT_SCOPE = re.compile(r"\b(?:second child|senior citizen|ha?emodialysis|peritoneal dialysis|"
                            r"plus|phase [iv\d]+|super[ -]specialt\w*)\b", re.I)
URL_FIELDS = ("application_url", "official_website", "source_url", "url")
REVIEWED_ALIASES = {
    "Ayushman Bharat PM-JAY (National Health Cover)": (
        "https://beneficiary.nha.gov.in/nha/NHA-data-privacy-policy.html",
        ("Ayushman Bharat - PM-JAY", "Ayushman Bharat - PMJAY (National Health Protection Mission)",
         "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)"),
    ),
    "Dr. NTR Vaidya Seva (AP Cashless Hospital Care)": (
        "https://svimstpt.ap.nic.in/annualreport_files/AR2024.pdf",
        ("Dr. YSR Aarogyasri", "Dr. NTR Vaidya Seva (Aarogyasri Health Scheme)"),
    ),
    "AP 108 Emergency Ambulance Service": (
        "https://hmfw.ap.gov.in/108-call-center.aspx",
        ("108 Emergency Medical Services", "108 Emergency Ambulance Medical Service"),
    ),
    "National Programme for Control of Blindness (NPCBVI)": (
        "https://dghs.mohfw.gov.in/opthalmology-division.php",
        ("National Programme for Control of Blindness & Visual Impairment (NPCBVI)",),
    ),
    "National Oral Health Programme": (
        "https://www.dghs.mohfw.gov.in/national-oral-health-division.php",
        ("National Oral Health Programme (NOHP - Dental Care)",),
    ),
    "Rashtriya Bal Swasthya Karyakram (Child Health Screening)": (
        "https://nhm.gov.in/images/pdf/programmes/child-health/guidelines/Rastriya-Bal-Swasthya-Karyakram%28RBSK%29.pdf",
        ("Rashtriya Bal Swasthya Karyakram (RBSK - Child Health Screening)",),
    ),
    "Assistance to Persons with Disabilities for Purchase or Fitting of Aids and Appliances (ADIP)": (
        "https://depwd.gov.in/en/adip/",
        ("Assistance to Disabled Persons for Purchase/Fitting of Aids (ADIP Scheme)",),
    ),
    "Ni-kshay Poshan Yojana (TB Nutrition Support)": (
        "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2200795",
        ("Ni-kshay Poshan Yojana (TB Financial & Nutritional Support)",),
    ),
}


def normalized_title(value):
    return "".join(
        char for char in unicodedata.normalize("NFKC", value).casefold()
        if char.isalnum() or unicodedata.category(char).startswith("M")
    )


def without_region(title, region):
    return re.sub(rf"\s*\(\s*{re.escape(region)}\s*\)$", "", title, flags=re.I) if region else title


def title_tokens(title):
    return set(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", title).casefold())) - STOP_WORDS


def urls(record):
    values = [record.get(field) for field in URL_FIELDS]
    values.append(((record.get("operations") or {}).get("application_process") or {}).get("official_url"))
    results = set()
    for value in values:
        if not isinstance(value, str):
            continue
        try:
            url = urlsplit(value)
        except ValueError:
            continue
        if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password:
            continue
        host = url.hostname.removeprefix("www.")
        query = tuple(sorted((key, value) for key, value in parse_qsl(url.query) if not key.startswith("utm_")))
        results.add((host, url.path.rstrip("/"), query))
    return results


def acronyms(title):
    return {normalized_title(value) for value in re.findall(r"\b[A-Z][A-Z0-9-]{3,}\b", title)
            if normalized_title(value) not in {"national", "andhra", "pradesh"}}


def resolve_identity(title, record, catalog, url_owners):
    region = record.get("level") or ""
    key = normalized_title(title)
    root_key = normalized_title(without_region(title, region))
    incoming_urls = urls(record)
    incoming_tokens = title_tokens(title)
    telugu = record.get("telugu_name") or ""
    confirmed, possible = [], []
    for name, current in catalog.items():
        if not region or normalized_title(region) != normalized_title(current.get("level") or ""):
            continue
        tokens = title_tokens(name)
        shared = tokens & incoming_tokens
        score = len(shared) / max(len(tokens | incoming_tokens), 1)
        current_urls = urls(current)
        shared_urls = incoming_urls & current_urls
        same_domain = bool({url[0] for url in incoming_urls} & {url[0] for url in current_urls})
        specific_page = any((url[1] or url[2]) and url_owners[url] == {name} for url in shared_urls)
        shared_acronym = bool(acronyms(name) & acronyms(title))
        source, reviewed = REVIEWED_ALIASES.get(name, (None, ()))
        if key == normalized_title(name):
            evidence = (4, "exact_title", None)
        elif root_key == normalized_title(without_region(name, region)):
            evidence = (3, "region_suffix_alias", None)
        elif root_key in {normalized_title(alias) for alias in reviewed}:
            evidence = (3, "reviewed_alias", source)
        elif DISTINCT_SCOPE.findall(title.lower()) != DISTINCT_SCOPE.findall(name.lower()):
            evidence = None
        elif specific_page and re.search(r"[ఀ-౿]", telugu) and (
            normalized_title(telugu) == normalized_title(current.get("telugu_name") or "")
        ):
            evidence = (2, "scheme_url_and_telugu_title", None)
        elif specific_page and len(shared) >= 2 and score >= 0.45:
            evidence = (2, "scheme_url_and_title", None)
        elif same_domain and shared_acronym and len(shared) >= 3 and (
            score >= 0.60 or title_tokens(title.split(" (", 1)[0]) == title_tokens(name.split(" (", 1)[0])
        ):
            evidence = (2, "portal_title_and_acronym", None)
        elif root_key in {normalized_title(without_region(alias, region)) for alias in current.get("aliases") or []}:
            evidence = (1, "stored_alias", None)
        else:
            evidence = None
        if evidence:
            confirmed.append((*evidence, name))
        if (len(shared) >= 2 and score >= 0.28) or shared_acronym:
            possible.append((score, name, same_domain, specific_page))
    if confirmed:
        best = max(item[0] for item in confirmed)
        winners = [item for item in confirmed if item[0] == best]
        if len(winners) == 1:
            _, method, source, name = winners[0]
            return name, method, source, []
        return None, "ambiguous_identity", None, [{"title": item[3]} for item in winners]
    return None, "needs_identity_review" if possible else "no_candidate", None, [
        {"title": name, "token_similarity": round(score, 3), "shared_domain": domain, "shared_scheme_url": page}
        for score, name, domain, page in sorted(possible, reverse=True)[:3]
    ]
