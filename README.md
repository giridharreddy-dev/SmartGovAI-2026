# SmartGovAI — SmartGov Health

[![pytest](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml/badge.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml)

SmartGovAI is an offline-first Progressive Web App and lightweight Flask backend designed to help low-literacy users discover and understand government health schemes in a simple, accessible way. The project combines a Telugu-first user experience with optional AI-assisted PDF simplification, deterministic audio generation, and local persistence for a practical public-service experience.

---

## Features

- Offline-first PWA experience with service worker caching for reliable access
- Telugu-first interface with audio support using gTTS or browser-based text-to-speech
- PDF text extraction with OCR fallback for broader document compatibility
- Optional AI-powered PDF simplification through Google Gemini
- Deterministic audio caching to reuse generated MP3 files efficiently
- Safe file uploads with server-side PDF validation
- Minimal Flask API for scheme lookup, eligibility checks, sharing, and feedback

---

## Why this project matters

- Supports citizens who may face language or digital barriers when navigating welfare programs
- Keeps essential functionality usable even with limited connectivity
- Demonstrates a practical, user-centered application of AI and accessibility principles
- Offers a strong example of a full-stack, portfolio-ready Flask + PWA project

---

## Tech Stack

- Python 3.10+ (Flask)
- google-genai (optional, Gemini)
- pdfplumber + pytesseract (optional OCR)
- gTTS for audio generation
- SQLite for local persistence
- Service worker + PWA for offline UX

---

## Project Status

- Status: ✅ Portfolio-ready
- Current version: 1.0.0
- Last tested: Python 3.14
- Test coverage: Current test coverage exceeds 80%

---

## Project Statistics

- Language: Python
- Framework: Flask
- Test Framework: pytest
- Database: SQLite
- Offline Support: Yes
- OCR Support: Yes
- AI Integration: Optional

---

## Key Engineering Highlights

- Offline-first Progressive Web App
- OCR fallback for scanned PDFs
- AI-assisted simplification using Gemini
- Telugu audio generation
- Deterministic caching for AI responses and audio
- Comprehensive automated test suite
- Structured logging
- Secure file upload validation

---

## Architecture

```mermaid
flowchart LR
    Browser -->|HTTP(S)| ServiceWorker[Service Worker]
    ServiceWorker --> FlaskAPI[Flask API]
    FlaskAPI --> DB[(SQLite)]
    FlaskAPI -->|calls| Gemini["Google Gemini (optional)"]
    FlaskAPI -->|OCR fallback| OCR[OCR Pipeline]
    FlaskAPI -->|audio cache| AudioCache[/static/audio/]
    subgraph Offline
        ServiceWorker
        AudioCache
    end
```

---

## Folder structure

```
.
├── app.py                  # Flask server and API endpoints
├── generate_audio.py       # Audio generation utility
├── view_db.py              # Local database inspection utility
├── services/               # App services (gemini, pdf, audio)
├── static/                 # Frontend assets and generated audio
│   └── audio/             # Generated MP3 audio files
├── templates/              # Jinja2 templates
├── schemes_complex.json    # Scheme definitions and content
├── database.py             # SQLite helper functions
├── requirements.txt        # Python dependencies
├── tests/                  # Pytest unit tests
├── scripts/                # Additional utility scripts
├── uploads/                # Uploaded PDF files
└── audio/                  # Local audio assets folder
```

---

## Environment variables

Create a `.env` file in the project root or provide env vars from your runtime environment.

- `SECRET_KEY` (required) — Flask secret for session management. Must be set in production.
- `GEMINI_API_KEY` (optional) — API key to enable PDF simplification via Google Gemini.
- `DB_PATH` (optional) — Path to the SQLite database file; default configured in `config.py`.

Do not commit secrets to the repository or logs.

---

## Installation (local)

Prerequisites: Python 3.10+, pip

```bash
git clone https://github.com/giridharreddy-dev/SmartGovAI-2026.git
cd SmartGovAI-2026
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `SECRET_KEY` (and `GEMINI_API_KEY` if you want AI features).

### Generate or reuse audio (optional)

To pre-generate MP3s for offline use:

```bash
python scripts/generate_audio.py
```

---

## Testing

Current results:

- ✅ 21 unit tests passing
- ✅ 82% code coverage
- ✅ Python 3.14 verified

Run the test suite with pytest:

```bash
pytest
```

Unit tests cover core service behaviors (Gemini parsing, audio naming, PDF handling).

---

## API documentation (selected endpoints)

- `POST /simplify` — Accepts uploaded PDF as `document` form file or JSON `scheme_name` to return simplified scheme. Returns JSON with `simplified`, `telugu`, and `voice_url` fields.
- `POST /eligibility-check` — JSON body `{ "scheme_name": "...", "answers": {...} }` returns eligibility percentage.
- `POST /whatsapp-share` — JSON `{ "scheme_name": "..." }` returns a WhatsApp share URL and message text.
- `POST /staff-report` — JSON report from staff with `scheme_name` and `feedback_type`.
- `GET /healthz` — Service health; includes directory & AI availability checks.

Most endpoints return JSON objects. Success responses include metadata such as `api_name`, `api_version`, `api_description`, `status`, and endpoint-specific fields, while error responses use a consistent `status: "error"` payload with `error_code` when applicable.

---

## Deployment checklist

1. Set `SECRET_KEY` in environment; never store in repo.
2. Configure a reverse proxy (Nginx) for TLS termination and HSTS.
3. Configure CSP/HSTS at the proxy (application sets minimal security headers but tune proxy for HSTS).
4. Use process manager (systemd / supervisor / gunicorn) to run the Flask app.
5. Configure logging to send errors to central logging (avoid logging env secrets).
6. Limit upload size and enable rate-limiting / WAF for public deployments.

Example Gunicorn run:

```bash
gunicorn app:app -w 4 -b 0.0.0.0:5000
```

For production deployments, use Gunicorn behind Nginx on Linux. Windows users can also run the app directly:

```bash
python app.py
```

---

## Screenshots

Suggested screenshots to add in the future:

- Home page
- Scheme search experience
- Eligibility checker
- PDF upload flow
- AI simplified result view
- Telugu audio playback
- Offline mode

---

## Engineering Challenges Solved

- Reused AI responses through deterministic caching
- Reused generated audio instead of regenerating files
- Added OCR fallback for scanned government PDFs
- Improved upload security through server-side PDF validation
- Added structured logging for easier debugging
- Supported offline usage with service workers

---

## Engineering Audit

An engineering audit for this project is available in [docs/ENGINEERING_AUDIT.md](docs/ENGINEERING_AUDIT.md).

---

## Future improvements

- Add server-side virus scanning for uploads
- Harden CSP and move to proxy configuration
- Add rate-limiting for expensive endpoints
- Add integration tests for the API + CI pipeline
- Provide pre-built Docker Compose for production stack

---

## Support & Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and developer setup.

---

## Credits

Developed as an academic and portfolio project focused on improving access to government health information through accessible technology.