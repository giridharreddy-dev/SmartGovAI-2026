# SmartGovAI

[![pytest](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml/badge.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-73%25-green.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)

## Table of Contents
1. [Abstract/Overview](#abstractoverview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Tech Stack](#tech-stack)
5. [Features](#features)
6. [System Setup/Installation](#system-setupinstallation)
7. [API Endpoints](#api-endpoints)
8. [Future Scope](#future-scope)

---

## Abstract/Overview

**SmartGovAI** is an offline-first Progressive Web Application (PWA) supported by a Python Flask backend, designed to mitigate the digital divide. It empowers citizens with limited literacy in rural Andhra Pradesh to discover, evaluate eligibility for, and comprehend government health and welfare schemes through a highly accessible, language-first interface.

The application combines a Telugu-centric, touch-accessible user experience with optional artificial intelligence-assisted policy document simplification, deterministic audio pre-caching, and client-side data persistence. This approach ensures a robust, public-service-grade experience tailored to regions with intermittent internet connectivity.

---

## Problem Statement

Rural citizens in India, particularly those with limited literacy and digital exposure, face significant barriers when attempting to access government welfare programs. Complex bureaucratic language, poor digital infrastructure, and a lack of regional language support often prevent eligible individuals from utilizing health schemes designed for their benefit. Current centralized digital portals typically require high-speed internet, advanced digital literacy, and English proficiency, rendering them ineffective for the target demographic.

---

## Objectives

1. **Accessibility Improvement:** To provide a Telugu-first platform with text-to-speech audio guidance for users with limited reading capabilities.
2. **Offline Resilience:** To engineer an architecture capable of operating in low-bandwidth or offline environments utilizing local caching and pre-generated audio.
3. **Comprehension Enhancement:** To translate and simplify complex government policy documents into plain, direct summaries.
4. **Data Privacy:** To ensure zero-trust client data storage, maintaining user anonymity by processing eligibility and checklists entirely on the client side without storing personally identifiable information (PII).

---

## Tech Stack

The application employs a decoupled client-server architecture:

### Client-Side
* **Markup and Styling:** HTML5, Vanilla CSS3 (App Shell)
* **Logic:** ES6+ JavaScript (`enhanced-features.js`)
* **Persistence:** `localStorage` (Answers, Documents)
* **Accessibility:** Web Speech API (Telugu Text-to-Speech)
* **Offline Management:** Service Worker (Stale-While-Revalidate caching strategy)
* **Maps:** Leaflet.js (Interactive healthcare facility maps)

### Server-Side
* **Framework:** Python 3.10+ with Flask
* **Database:** SQLite (`feedback.db`)
* **File Parsing:** `pdfplumber` with Tesseract OCR fallback
* **Audio Generation:** gTTS (Google Text-to-Speech)
* **Artificial Intelligence:** Google Gemini API (`gemini-3.5-flash`)
* **QR Codes:** `qrcode[pil]` (Dynamic scheme QR code generation)
* **Security & Rate Limiting:** Flask-Limiter, Redis, Flask-WTF
* **Production Server:** Gunicorn (Linux/macOS)

### Infrastructure
* **Containerization:** Docker, Docker Compose
* **CI/CD:** GitHub Actions (pytest workflow)

---

## Repository Structure

```text
SmartGovAI-2026/
├── .github/workflows/    # CI/CD pipelines
├── data/                 # JSON scheme definitions
├── docs/                 # Detailed technical documentation
├── scripts/              # Utility scripts (e.g., generate_audio.py)
├── services/             # Core backend logic (audio, chat, Gemini, PDF, QR)
├── static/               # Frontend assets (CSS, JS, Service Worker)
├── templates/            # HTML/Jinja2 templates
├── tests/                # Pytest suite
├── app.py                # Main Flask application and routing
├── database.py           # SQLite database setup and helper functions
├── requirements.txt      # Python dependencies
└── config.py             # Environment configuration parser
```

---

## Features

* **Modular Scheme Loading:** During application startup, the server dynamically scans the `data/` directory, validates JSON entries against structural schema constraints, and merges valid schemes into a single in-memory catalog.
* **AI Chat Assistant:** A Telugu-language RAG (Retrieval-Augmented Generation) chat assistant that answers citizen questions using grounded scheme data, with strict guardrails against hallucination and system prompt leakage.
* **Artificial Intelligence Simplification:** Extends Google Gemini API to parse complex policy documents, extracting relevant eligibility and benefit criteria and translating them into simple Telugu.
* **Healthcare Facilities GIS Locator:** Interactive Leaflet.js map with 400+ AP healthcare facilities (PHC, CHC, Hospitals), GPS-based proximity search via Haversine distance calculation.
* **Scheme Deep Links & QR Codes:** Human-readable URL slugs (`/scheme/<slug>`) and on-the-fly QR code PNG generation (`/qr/<slug>.png`) for field distribution and flyer printing.
* **Impact Analytics Dashboard:** Admin-protected dashboard (`/analytics`) with aggregate, anonymized usage metrics, secured via Bearer token and session-based authentication.
* **Deterministic Audio Caching:** Pre-renders audio MP3 assets for all schemes. It only initiates an external Text-to-Speech call when a cache miss occurs, conserving bandwidth and ensuring immediate availability.
* **WhatsApp & SMS Sharing:** Pre-formatted WhatsApp message generation and SMS intent triggers for viral, frictionless information propagation through social networks.
* **ASHA/Field Staff Reporting:** Dedicated interface for community health workers to report discrepancies, add local details, and manage scheme information.
* **Enterprise-Grade Security:** Implements Cross-Site Request Forgery (CSRF) protection, Content Security Policy (CSP) headers with per-request nonces, strict HTTP headers, and robust file upload validation (including magic byte verification and consent-gated PDF processing).
* **Resilient Rate Limiting:** Utilizes an in-memory tracking fallback mechanism if the primary Redis server becomes unavailable, guaranteeing continuous availability.

---

## Documentation

Detailed technical documentation can be found in the `docs/` directory:
* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture, folder structure, and technical execution flows.
* [`docs/FEATURES_IMPLEMENTED.md`](docs/FEATURES_IMPLEMENTED.md) - Deep dive into all implemented features.
* [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) - Detailed guide on how citizens use the application.
* [`docs/EXECUTION_FLOW.md`](docs/EXECUTION_FLOW.md) - Sequence diagrams for request routing and parsing.
* [`docs/CHANGELOG.md`](docs/CHANGELOG.md) - Version history and historical bug fixes.
* [`docs/IMPLEMENTATION_LOG.md`](docs/IMPLEMENTATION_LOG.md) - Development implementation log.
* [`docs/ENGINEERING_AUDIT.md`](docs/ENGINEERING_AUDIT.md) - Pre-deployment technical review findings.

---

## System Setup/Installation

### Prerequisites
* Python 3.10+
* `pip` and `virtualenv`
* *Optional:* Tesseract-OCR and Poppler binaries installed on the system path for advanced PDF parsing.

### Quick Start

**Option 1: One-click setup scripts**
```bash
# Windows
setup.bat

# macOS / Linux
chmod +x setup.sh && ./setup.sh
```

**Option 2: Docker**
```bash
docker compose up --build
```

**Option 3: Manual setup**

1. Clone the repository and navigate to the directory:
   ```bash
   git clone https://github.com/giridharreddy-dev/SmartGovAI-2026.git
   cd SmartGovAI-2026
   ```

2. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY and ADMIN_TOKEN (see below)
   ```

3. Establish and activate the virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate       # Windows PowerShell
   source .venv/bin/activate      # macOS / Linux
   ```

4. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Pre-generate the audio files:
   ```bash
   python -m scripts.generate_audio
   ```

6. Launch the application server:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://localhost:5000`.

### Environment Configuration

Configure the required parameters by adding them to the local `.env` file:

```bash
# ── Required ──────────────────────────────────────────────
SECRET_KEY=your-secret-key         # Flask session encryption — generate with: python -c "import secrets; print(secrets.token_hex(32))"
ADMIN_TOKEN=your-admin-token       # Bearer token for /analytics — generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# ── Optional (defaults shown) ────────────────────────────
GEMINI_API_KEY=                    # Enables AI PDF simplification and chat responses
DB_PATH=feedback.db                # SQLite database path
REDIS_URL=                         # e.g. redis://localhost:6379/0 — falls back to in-memory if unset
TRUSTED_PROXIES=0                  # Number of upstream reverse proxies (e.g. 1 behind Nginx/Cloudflare)

# ── Rate Limiting ────────────────────────────────────────
RATELIMIT_DEFAULT=200 per day; 50 per hour
RATELIMIT_SIMPLIFY=10 per minute; 60 per hour
RATELIMIT_FEEDBACK=20 per minute
RATELIMIT_REPORT=10 per minute
RATELIMIT_CHAT=15 per minute; 100 per hour
```

> **Note:** `SECRET_KEY` is mandatory — the application will not start without it. `GEMINI_API_KEY` is optional; without it, the app runs in catalog-only mode (no AI chat or PDF simplification).

### Testing
To execute the automated test suite and review code coverage:
```bash
pytest
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | `GET` | Primary application shell |
| `/chat` | `POST` | AI chat assistant with Telugu RAG retrieval |
| `/simplify` | `POST` | PDF simplification / catalog scheme simplification |
| `/scheme/<slug>` | `GET` | Deep link to a specific scheme |
| `/qr/<slug>.png` | `GET` | QR code PNG for a scheme |
| `/api/facilities` | `GET` | Healthcare facilities with GPS distance |
| `/analytics` | `GET` | Admin Impact Dashboard (protected) |
| `/admin/login` | `GET, POST` | Admin authentication |
| `/admin/logout` | `GET` | Admin session termination |
| `/eligibility-check` | `POST` | Eligibility evaluation |
| `/document-checklist` | `GET` | Document requirements |
| `/whatsapp-share` | `POST` | WhatsApp sharing |
| `/feedback` | `POST` | User feedback |
| `/enhanced-feedback` | `POST` | Detailed user feedback |
| `/staff-report` | `POST` | Field staff reports |
| `/local-locations` | `GET` | Local service information |
| `/offline-cache` | `GET` | Full catalog for PWA caching |
| `/healthz` | `GET` | Health check |
| `/health` | `GET` | Health check alias |
| `/version` | `GET` | API version and metadata |
| `/offline.html` | `GET` | Offline fallback page |

---

## Future Scope

Subsequent iterations of the SmartGovAI system may address the following objectives:
* **Asynchronous Processing:** Transitioning AI simplification and audio generation tasks to an asynchronous message queue (e.g., Celery) to prevent thread blocking under high concurrent loads.
* **Modular Refactoring:** Restructuring the monolithic routing file into Flask Blueprints to isolate responsibilities and improve maintainability as the application scales.
* **Expanded Linguistic Support:** Extending the translation and text-to-speech architecture to accommodate additional regional languages to broaden accessibility across different states.
* **Enhanced Observability:** Integrating application performance monitoring and structured log aggregation for production deployments.
* **API Documentation:** Generating OpenAPI/Swagger specifications for all endpoints.