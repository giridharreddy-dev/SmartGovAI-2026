# Data Provenance Audit

This document reviews the state of data provenance within the SmartGovAI repository's static datasets (`data/`).

## Audit Findings Checklist

1. **Exact scheme datasets**: `data/national_and_ap_schemes.json`, `data/extra_schemes.json`, `data/health.json`
2. **Exact facility dataset**: `data/facilities.json` (1,485 records)
3. **Existing provenance fields**: `source_url`, `source_name`, and `last_updated` are defined in the schema.
4. **Missing provenance fields**: Specific cryptographic hashes, individual verifier IDs, and explicit retrieval timestamps.
5. **Whether source URLs exist**: Yes, most scheme records contain a `source_url`. Facility records do not.
6. **Whether retrieval dates exist**: No, only generic `last_updated` dates are currently stored.
7. **Whether verification identities exist**: No, it is not recorded *who* manually entered or verified the data.
8. **Whether dataset versioning exists**: No formal dataset versioning exists outside of standard Git commits.
9. **Risks of stale government information**: Significant risk. Without live API integration, static JSON data will eventually drift from actual policy, potentially misleading users.
10. **Recommended future provenance schema**:

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
