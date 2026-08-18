# Data Provenance Audit

This document reviews the state of data provenance within the SmartGovAI repository's static datasets (`data/`).

## Audit Findings

### 1. Scheme Definitions (`data/national_and_ap_schemes.json`, `data/extra_schemes.json`, `data/health.json`)
The application relies on static JSON files to define welfare schemes. 

**Current Provenance State:**
- The schema (`scheme_schema.json`) includes fields such as `source_url`, `source_name`, and `last_updated`.
- Many schemes contain descriptions of official government targets (e.g., "100% household access" for NIDDCP or "50% to 90% cheaper" for PMBJP). These represent official government objectives extracted from source material, **not** the measured impact of the SmartGovAI application.
- **Gaps:** Specific retrieval dates, the exact individuals who verified the data, and versioning hashes of the original government PDFs are generally not documented in the repository.

### 2. Healthcare Facilities (`data/facilities.json`)
The application loads over 1,480 healthcare facilities for the geospatial locator.

**Current Provenance State:**
- The file contains coordinates (lat/lng), names, and types of facilities.
- **Gaps:** The original source organization (e.g., Ministry of Health and Family Welfare API, OpenStreetMap, or manual compilation) and the specific URL from which this data was obtained are **not documented in the repository**. We cannot objectively guarantee the freshness or completeness of this facility list.

## Recommended Provenance Schema (Future Work)

To ensure academic rigor and public trust, future iterations of this project should enforce a strict provenance wrapper around all data entries. 

**Proposed standard for JSON records:**
```json
{
  "provenance": {
    "source_organization": "Official Govt Dept",
    "source_url": "https://...",
    "retrieved_at": "2026-06-01T10:00:00Z",
    "last_verified_by": "username",
    "verification_status": "verified",
    "original_document_hash": "sha256..."
  }
}
```

## Conclusion
Currently, SmartGovAI relies on statically compiled JSON files. While some fields indicate their source URLs, comprehensive cryptographic and temporal provenance tracking is missing. Users must be explicitly warned that data might be outdated, and the project must not claim official government partnership unless a live, authenticated API integration is achieved.
