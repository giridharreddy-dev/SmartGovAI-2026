# Version History

All notable technical modifications to the SmartGovAI repository are documented chronologically in this file.

The versioning format complies with the "Keep a Changelog" standard and adheres to Semantic Versioning principles where applicable.

## [1.0.0] - 2026-08-14

### Added
- **AI Chat Assistant**: Grounded RAG (Retrieval-Augmented Generation) chat endpoint (`/chat`) using Gemini 3.5 Flash with Telugu alias expansion, token scoring, and strict anti-hallucination guardrails. Catalog-only fallback when Gemini is unavailable.
- **Healthcare Facilities GIS Locator**: API endpoint (`/api/facilities`) serving 400+ AP healthcare facilities with GPS-based Haversine distance sorting. Interactive Leaflet.js map with facility type filtering.
- **Scheme Deep Links**: Human-readable URL slugs (`/scheme/<slug>`) with deterministic SHA-256 hashing for stable URLs.
- **QR Code Generation**: On-the-fly PNG generation endpoint (`/qr/<slug>.png`) using `qrcode[pil]` for field distribution flyers.
- **Impact Analytics Dashboard**: Admin-protected dashboard (`/analytics`) with aggregate usage metrics. Dual authentication via Bearer token header or session cookie (`/admin/login`, `/admin/logout`).
- **Docker Containerization**: `Dockerfile` with dynamic `$PORT` binding and `docker-compose.yml` for multi-service orchestration.
- **GitHub Actions CI**: Automated pytest workflow (`.github/workflows/pytest.yml`).
- **Frontend Contract Tests**: Behavioral regression tests (`tests/test_frontend_contract.py`) validating UI invariants: filter button state, scroll-to-top, chat handlers, mobile layout ordering.
- **Chat Client UI**: Complete chat overlay with open/close/send handlers, keyboard shortcuts (Escape, Ctrl+Enter), suggestion buttons, and event delegation in `enhanced-features.js`.

### Fixed
- **Static Audio URL Double-Prefix**: `/offline-cache` was returning `/static/static/audio/...` paths; corrected with `removeprefix("static/")`.
- **HTTP Exception Status Preservation**: Global error handler now preserves intentional HTTP error codes (e.g., 429 Too Many Requests) instead of rewriting all exceptions to 500.
- **Facilities Negative Radius**: `/api/facilities` now rejects negative `radius` query parameters with a 400 error.
- **Dockerfile Port Binding**: Changed from hardcoded `:5000` to `${PORT:-5000}` for Render and PaaS compatibility.
- **CSS Media Query Brace Imbalance**: Corrected misplaced closing brace that trapped dashboard/chat/map styles inside a `@media (max-width: 414px)` block.
- **"అన్నీ" Filter Button Highlight**: Removed hardcoded `active` class; button now styled dynamically via JavaScript.
- **Scheme Details Scroll Position**: Added `scrollIntoView({ behavior: 'smooth', block: 'start' })` with `prefers-reduced-motion` respect.
- **External URL Validation**: `safe_url()` now rejects non-HTTP schemes and URLs without a valid netloc.

### Security
- Consent-gated PDF upload pipeline with explicit user acknowledgment before AI processing.
- PDF magic byte verification (`%PDF` header check) before file processing.
- Response sanitization in chat to prevent system prompt leakage and API key exposure.
- CSRF protection on all mutable endpoints with per-request CSP nonces.

## [0.2.0] - 2026-07-09

- **Security Hardening**: Implemented server-side PDF magic byte header validation and reinforced HTTP response security headers (Phase 4.4).
- **Documentation**: Revised the README file to include an architectural overview and a formalized deployment validation checklist.

## [0.1.0] - 2026-06-15

- **Performance Optimization**: Engineered Gemini API response caching, implemented duplicate-request blocking via thread locks, and introduced deterministic hashing for audio filenames to minimize redundant processing (Phase 4.3).
- **Defect Resolution**: Engineered a graceful fallback mechanism to circumvent `AttributeError` exceptions during automated testing when Google Generative AI types are unresolvable.

## Initial Development

- Bootstrapped the initial repository scaffolding, integrating the Progressive Web Application (PWA) client interface with the underlying Python Flask backend services.
