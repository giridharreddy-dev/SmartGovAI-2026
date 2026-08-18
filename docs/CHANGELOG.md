# Version History

All notable technical modifications to the SmartGovAI repository are documented chronologically in this file.

The versioning format complies with the "Keep a Changelog" standard and adheres to Semantic Versioning principles where applicable.

## [1.0.0] - 2026-08-14

### Documentation (August 2026 Audit)
- **Comprehensive Audit**: Executed a 19-phase documentation audit ensuring strict parity between source code and documentation.
- **Academic Restructuring**: Formalized `README.md`, `PROJECT_PROPOSAL.md`, and `IMPACT_EVALUATION.md` to clearly delineate implemented features from proposed studies.
- **Data Provenance Strategy**: Defined a 10-point provenance evaluation schema in `DATA_PROVENANCE.md` to track government data origin.

### Added
- **AI Chat Assistant**: Grounded RAG (Retrieval-Augmented Generation) chat endpoint (`/chat`) using Gemini 3.5 Flash with Telugu alias expansion, token scoring, and strict anti-hallucination guardrails. Catalog-only fallback when Gemini is unavailable.
- **Healthcare Facilities GIS Locator**: API endpoint (`/api/facilities`) serving 1,480+ AP healthcare facilities with GPS-based Haversine distance sorting. Interactive Leaflet.js map with facility type filtering.
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


## Historical Bug Fixes

### Software Defect Resolutions: HTML and JavaScript Components

#### Resolved Issues

##### 1. **Variable Scope Conflict Resolution**
**Problem Statement**: The variable `currentSchemeName` was declared in two separate execution contexts:
- Within the `index.html` script block: `let currentSchemeName = null;`
- Within the `enhanced-features.js` external script: `let currentSchemeName = null;`

This dual declaration generated a scope conflict, resulting in desynchronized state variables during runtime execution.

**Implementation Fix**:
- Removed the redundant declaration `let currentSchemeName = null;` from `enhanced-features.js`.
- Configured `index.html` to instantiate the variable at both the local and window scope levels to ensure global accessibility:
  ```javascript
  currentSchemeName = data.scheme_name;
  window.currentSchemeName = data.scheme_name;
  ```
- Updated all references in `enhanced-features.js` to explicitly utilize `window.currentSchemeName`.

##### 2. **Function Access Scope Correction**
**Problem Statement**: The `escapeHtml()` sanitization function, defined within the `index.html` script context, was inaccessible from the external `enhanced-features.js` script.

**Implementation Fix**:
- Modified all function invocations of `escapeHtml()` in `enhanced-features.js` to reference the global window object via `window.escapeHtml()`.
- Reference examples:
  - `${escapeHtml(value)}` was updated to `${window.escapeHtml(value)}`
  - `${escapeHtml(currentSchemeName)}` was updated to `${window.escapeHtml(window.currentSchemeName)}`

##### 3. **Global Request ID Accessibility**
**Problem Statement**: The `currentRequestId` variable referenced in `enhanced-features.js` failed to access the dynamically assigned value established within `index.html`.

**Implementation Fix**:
- Standardized variable references to explicitly use `window.currentRequestId`.
- Ensured the `displayResult` execution block in `index.html` formally assigns the data ID: `window.currentRequestId = data.request_id`.

#### Modified Source Files

1. **templates/index.html**
   - Introduced `let currentSchemeName = null;` preceding the `escapeHtml` function declaration.
   - Refactored the `displayResult()` function to explicitly set both local and window-scoped context variables.
   - Verified that the hierarchical script loading order was maintained correctly.

2. **static/enhanced-features.js**
   - Eliminated the duplicate `let currentSchemeName = null;` declaration.
   - Prefixed all `escapeHtml()` invocations with the `window` object.
   - Prefixed all `currentSchemeName` references with the `window` object.
   - Updated the `sendDetailedFeedback()` function to accurately reference `window.currentRequestId`.

#### Verification and Testing Protocol
- [ ] Application instantiation sequence completes without console errors.
- [ ] Selecting a scheme renders the complete data schema and activates all associated features.
- [ ] The Eligibility Checker component initializes without throwing scope exceptions.
- [ ] The Document Checklist component initializes without throwing scope exceptions.
- [ ] The external WhatsApp sharing trigger executes successfully.
- [ ] The user feedback endpoints trigger and resolve successfully.
- [ ] The browser developer console remains devoid of undefined reference exceptions.

---

### Phase 5: Backend, Security & Deployment Fixes

#### 4. **Static Audio URL Double-Prefix**
**Problem Statement**: The `/offline-cache` endpoint returned audio paths prefixed as `/static/static/audio/...` instead of `/static/audio/...`, causing broken audio playback in cached/offline mode.

**Implementation Fix**: Applied `removeprefix("static/")` to audio paths before prepending the `/static/` URL prefix.

#### 5. **HTTP Exception Status Preservation**
**Problem Statement**: The global exception handler in `app.py` was rewriting all exceptions (including intentional HTTP errors like 429 Too Many Requests) to status 500.

**Implementation Fix**: Modified the handler to check for `werkzeug.exceptions.HTTPException` and preserve its original status code.

#### 6. **Facilities Negative Radius Validation**
**Problem Statement**: The `/api/facilities` endpoint accepted negative radius values, producing nonsensical search results.

**Implementation Fix**: Added server-side validation to reject negative `radius` query parameters with a 400 error.

#### 7. **Dockerfile Port Binding**
**Problem Statement**: The Dockerfile CMD was hard-coded to `gunicorn --bind 0.0.0.0:5000`, ignoring the `$PORT` environment variable required by Render and similar PaaS platforms, causing HTTP 502 errors.

**Implementation Fix**: Changed CMD to `sh -c "gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"` to respect the platform-assigned port.

#### 8. **CSS Media Query Brace Imbalance**
**Problem Statement**: A misplaced closing brace in `static/style.css` caused dashboard, chat, and map styles to be incorrectly scoped inside a `@media (max-width: 414px)` block, making them invisible on desktop.

**Implementation Fix**: Corrected the brace balance so all styles apply at their intended breakpoints.

#### 9. **Chat Endpoint Missing Client Handlers**
**Problem Statement**: The `/chat` backend route existed but had no corresponding client-side JavaScript to open the chat UI, send messages, or display responses.

**Implementation Fix**: Added complete chat UI handlers in `enhanced-features.js`: `openChat()`, `closeChat()`, `sendChatQuestion()`, `appendChatMessage()`, with keyboard shortcuts (Escape to close, Ctrl+Enter to send) and event delegation.

#### 10. **"అన్నీ" (All) Filter Button Persistent Highlight**
**Problem Statement**: The "అన్నీ" filter button remained visually highlighted/selected even when it should not have been.

**Implementation Fix**: Removed the hardcoded `active` class from the template. The button now receives the active style only through JavaScript when it is the actual active filter.

#### 11. **Scheme Details Scroll Position**
**Problem Statement**: When a user clicked on a scheme card, the page did not scroll to the scheme details area, leaving users stranded at their current scroll position.

**Implementation Fix**: Added `scrollIntoView({ behavior: 'smooth', block: 'start' })` on the result area after scheme selection, with `prefers-reduced-motion` respect.

#### Final Status
All identified scope and definition errors within the JavaScript components have been resolved. The application executes synchronously across both inline and external script boundaries.
