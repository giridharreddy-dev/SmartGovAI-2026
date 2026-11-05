"""Group unresolved V2 leads by reported department for editorial review."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

from scripts.merge_schemes import write_json

AP_HEALTH = "AP Health, Medical & Family Welfare"
AP_SECONDARY = "AP Directorate of Secondary Health (formerly APVVP)"
HEALTH_MINISTRY = "Ministry of Health and Family Welfare"
NHM = "National Health Mission"
NHA = "National Health Authority"
TB = "Central TB Division and state TB programmes"

EYE_TRUST = "AP NTR Vaidya Seva / Aarogyasri Trust"
DEPARTMENTS = {
    "aarogyasri.ap.gov.in": EYE_TRUST,
    "ehs.ap.gov.in": EYE_TRUST,
    "hmfw.ap.gov.in": AP_HEALTH,
    "cfw.ap.nic.in": AP_HEALTH,
    "nhm.gov.in": NHM,
    "tbcindia.gov.in": TB,
    "nikshay.in": TB,
    "communitysupport.nikshay.in": TB,
    "abdm.gov.in": NHA,
    "wcd.ap.gov.in": "AP Women Development and Child Welfare",
    "wdcw.ap.gov.in": "AP Women Development and Child Welfare",
    "apdascac.ap.gov.in": "AP Differently Abled and Senior Citizens Assistance Corporation",
    "cmrf.ap.gov.in": "AP Chief Minister's Relief Fund",
    "navasakam.ap.gov.in": "AP Rural Development / pension delivery",
    "sspensions.ap.gov.in": "AP Rural Development / pension delivery",
    "ayush.gov.in": "Ministry of AYUSH",
    "echs.gov.in": "Ministry of Defence",
    "esic.gov.in": "Employees' State Insurance Corporation",
    "cghs.nic.in": HEALTH_MINISTRY,
}
MENTAL_HEALTH_SOURCE = "https://www.dghs.mohfw.gov.in/national-mental-health-programme.php"
NHM_SOURCE = "https://www.nhm.gov.in/index1.php?lang=1&level=2&lid=192&sublinkid=1218"
AP_SECONDARY_SOURCE = "https://westgodavari.ap.gov.in/ap-vaidhya-vaidhan-parishaddchs/"


def department(record, host):
    source = (record.get("source_name") or "").casefold()
    if "apvvp" in source or "vaidya vidhana parishad" in source:
        return AP_SECONDARY
    if host in DEPARTMENTS:
        return DEPARTMENTS[host]
    if host.endswith((".mohfw.gov.in", ".nhp.gov.in")):
        return HEALTH_MINISTRY
    return record.get("source_name") or "Department unconfirmed"


def review(title, region, candidates):
    name = title.casefold()
    if "tele-manas" in name:
        return ("state_delivery" if region == "Andhra Pradesh" else "programme_component",
                "Tele-MANAS is the digital component of the National Mental Health Programme.", MENTAL_HEALTH_SOURCE)
    if "free diagnostic" in name or "free drugs service initiative" in name:
        return ("bundled_record" if " & " in title else "programme_component",
                "NHM describes diagnostics and medicines as service initiatives. Verify named test coverage and local delivery separately.",
                NHM_SOURCE)
    if "digital mission" in name and "abdm" in name:
        return ("standalone_programme",
                "NHA identifies ABDM as the broader digital mission and ABHA as one element. Keep ABDM separate from PM-JAY and ABHA.",
                "https://abdm.gov.in/strapicms/uploads/ABHA_Brochure_Piano_final_b972459053.pdf")
    if "health infrastructure mission" in name:
        return ("standalone_programme",
                "The Ministry describes PM-ABHIM as a health-infrastructure mission.",
                "https://www.mohfw.gov.in/sites/default/files/Final%20Printed%20English%20AR%202024-25.pdf")
    if "national dialysis programme" in name and region == "Andhra Pradesh":
        return ("state_delivery",
                "The V2 row names APVVP. The district directorate lists dialysis centres; local eligibility still needs confirmation.",
                AP_SECONDARY_SOURCE)
    if ("ntep" in name and "poshan" in name) or any(
        term in name for term in (" & family physician", " & village clinics", " & mukhyamantri bal")
    ):
        return ("bundled_record", "The title names more than one intervention or benefit. Verify each relationship before splitting.", None)
    if region == "Andhra Pradesh" and any(term in name for term in (
        "pmmvy - ap", "esanjeevani ap", "nvhcp - ap", "suman scheme - ap", "rksk - ap",
        "ap home-based care", "ap ntcp clinics",
    )):
        return ("state_delivery_candidate", "The title names a state implementation of a broader programme. Verify its local rules.", None)
    if any(term in name for term in (
        "post-operative", "post-op", "free knee", "free cancer", "thalassaemia", "thalassemia",
        "advanced scans", "peritoneal dialysis", "tiffa", "super-specialty", "screening",
        "tele-consultation", "tele-ophthalmology", "medical teams",
    )):
        return ("programme_component_candidate", "The record describes a service or procedure. Verify the parent package and scope.", None)
    if candidates:
        return ("identity_review", "Compare the ranked matches and scope before treating this as an alias or a component.", None)
    if any(term in name for term in ("scheme", "programme", "mission", "yojana", "relief fund", "pension")):
        return ("standalone_candidate", "The title names a programme or benefit. Verify its official identity and current status.", None)
    return ("insufficient_evidence", "The title and department do not identify a safe parent or standalone programme.", None)


def audit_pending(records):
    groups = defaultdict(list)
    categories = Counter()
    for row in records:
        record = row["v2_record"]
        region = record.get("level") or "Unspecified"
        url = record.get("official_website") or record.get("source_url") or ""
        host = (urlsplit(url).hostname or "").removeprefix("www.")
        classification, rationale, source = review(row["title"], region, row.get("candidates") or [])
        categories[classification] += 1
        groups[(region, department(record, host))].append({
            "title": row["title"], "identity_key": row["identity_key"], "classification": classification,
            "rationale": rationale, "official_evidence": source,
            "v2_reported_source": record.get("source_name"), "v2_portal": url,
            "candidate_parents": row.get("candidates") or [],
        })
    return {
        "summary": {
            "records": len(records), "identity_keys": len({row["identity_key"] for row in records}),
            "department_clusters": len(groups), "classification_counts": dict(sorted(categories.items())),
            "records_with_official_evidence": sum(bool(row["official_evidence"]) for rows in groups.values() for row in rows),
        },
        "clusters": [
            {"jurisdiction": region, "department": name, "record_count": len(rows), "records": rows}
            for (region, name), rows in sorted(groups.items())
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reconciliation_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.reconciliation_report.resolve():
        parser.error("The audit output needs its own path")
    report = json.loads(args.reconciliation_report.read_text(encoding="utf-8-sig"))
    audit = audit_pending(report["pending_review"])
    write_json(args.output, audit)
    print(json.dumps(audit["summary"], indent=2))


if __name__ == "__main__":
    main()
