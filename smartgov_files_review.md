# SmartGovAI: File Dictionary and Component Responsibility

## Table of Contents
1. [Summary Directory Table](#summary-directory-table)
2. [File-by-File Technical Review](#file-by-file-technical-review)

---

## 1. Summary Directory Table

| File Name | Architecture Type | Primary Purpose | Key Dependencies (Imports) | Imported By |
| :--- | :--- | :--- | :--- | :--- |
| **`app.py`** | Core File | Main controller and HTTP route dispatcher | `config`, `database`, `utils`, `gemini_service`, `pdf_service`, `audio_service`, `logger_config` | `tests/test_app.py` |
| **`database.py`** | Core File | Database persistence layer (SQLite) | `logger_config` | `app.py`, `tests/test_app.py` |
| **`services/audio_service.py`** | Core File | Auditory synthesis generator (gTTS) | None | `app.py`, `generate_audio.py`, `tests/test_audio_service.py` |
| **`services/gemini_service.py`** | Core File | AI Policy simplification integration | `config` | `app.py`, `tests/test_gemini_service.py` |
| **`services/pdf_service.py`** | Core File | PDF character extraction and OCR fallback | `config` | `app.py`, `tests/test_pdf_service.py` |
| **`static/enhanced-features.js`** | Core File | Browser UI logic and persistent state caching | None | `templates/index.html` |
| **`templates/index.html`** | Core File | PWA application markup shell | `style.css`, `enhanced-features.js` | None (served by `app.py`) |
| **`config.py`** | Helper File | Environmental configuration parser | None | `app.py`, `gemini_service.py`, `pdf_service.py` |
| **`utils.py`** | Helper File | Security and upload validation algorithms | None | `app.py`, `tests/test_utils.py` |
| **`logger_config.py`** | Helper File | Standardized logging formatter | None | `app.py`, `database.py` |
| **`static/service-worker.js`** | Helper File | Offline PWA caching strategy controller | None | `enhanced-features.js` (registration) |
| **`scripts/generate_audio.py`** | Helper File | Offline bulk TTS pre-rendering CLI script | `app`, `audio_service` | None |

---

## 2. File-by-File Technical Review

### `app.py`
* **Classification**: Core File
* **Purpose**: Operates as the primary entry point and web controller, routing all HTTP traffic for the application.
* **Responsibilities**:
  * Initializes the Flask application context, CSRF token verification middleware (`Flask-WTF`), logging configurations, and client rate limits (`Flask-Limiter`).
  * Dynamically enumerates, validates, and ingests all `.json` files located within the `data/` directory during startup.
  * Exposes HTTP endpoints necessary for rendering the UI, executing document simplification, persisting client ratings, and serving audio binaries.
* **Major Functions**:
  * `load_schemes()`: Aggregates all JSON structures in `data/` into a single, unified memory dictionary.
  * `index()`: The standard HTML rendering controller for the root path (`/`).
  * `simplify()`: The RESTful `/simplify` POST handler responsible for processing text and file simplification requests.
  * `feedback_route()`: The RESTful `/feedback` POST handler responsible for persisting client quantitative feedback.
* **Imports Utilized**: `config.py`, `database.py`, `utils.py`, `services/gemini_service.py`, `services/pdf_service.py`, `services/audio_service.py`, `logger_config.py`.

### `database.py`
* **Classification**: Core File
* **Purpose**: Manages the local relational data persistence layer.
* **Responsibilities**:
  * Creates and maintains the underlying SQLite database file (`feedback.db`).
  * Defines and executes Data Definition Language (DDL) for all tables: `requests`, `feedback`, and `audit_logs`.
  * Manages thread-safe SQLite connection context managers.
* **Major Functions**:
  * `init_db()`: Initializes database tables.
  * `log_request()`: Persists request metadata and timing data.
  * `save_feedback()`: Instantiates connections and inserts user rating evaluations.
  * `log_audit()`: Formats and stores structured audit log entries.
* **Imports Utilized**: `logger_config.py`.

### `services/audio_service.py`
* **Classification**: Core File
* **Purpose**: Coordinates Telugu Text-to-Speech (TTS) binary generation.
* **Responsibilities**:
  * Converts translated text strings into audio summaries utilizing the `gTTS` library.
  * Implements network query rate throttling and connection retry buffers.
  * Skips rendering execution if the target summary is detected within the static cache.
  * Enforces disk footprint constraints by purging obsolete cached audio files.
* **Major Functions**:
  * `generate_audio_file()`: Fetches TTS streams and handles transient connection faults.
  * `cleanup_old_audio()`: Rotates the audio directory to mitigate storage overflow scenarios.

### `services/gemini_service.py`
* **Classification**: Core File
* **Purpose**: Integrates the Google Gemini AI language models for translation and policy simplification.
* **Responsibilities**:
  * Constructs system instructions coercing Gemini to return compliant JSON schemas.
  * Translates bureaucratic policy structures between English and simplified Telugu.
* **Major Functions**:
  * `simplify_policy_text()`: Interfaces with the Gemini SDK, performing structural validation.
* **Imports Utilized**: `config.py`.

### `services/pdf_service.py`
* **Classification**: Core File
* **Purpose**: Document extraction controller.
* **Responsibilities**:
  * Reads and extracts string characters from uploaded PDF attachments.
  * Executes a fallback sequence to Gemini vision models (OCR mode) when direct text extraction yields insufficient characters (indicating scanned image PDFs).
* **Major Functions**:
  * `extract_text_from_pdf()`: Direct character reading algorithm.
  * `perform_ocr_on_pdf()`: Visual layout rendering and OCR extraction via Gemini.
* **Imports Utilized**: `config.py`.

### `static/enhanced-features.js`
* **Classification**: Core File
* **Purpose**: Drives client-side Document Object Model (DOM) interactions and behaviors.
* **Responsibilities**:
  * Intercepts browser events to manage and display offline state flags.
  * Governs the dynamic form rendering for feedback and administrative reporting.
  * Renders eligibility forms and synchronizes checklist states with the `localStorage` API.
  * Protects AJAX POST requests by extracting and forwarding CSRF validation headers.
* **Major Namespaces**:
  * `SmartGovEnhanced`: A functional namespace encapsulating all UI initialization routines and event handlers.

### `templates/index.html`
* **Classification**: Core File
* **Purpose**: Defines the primary application user interface layout.
* **Responsibilities**:
  * Establishes the structural DOM layout (Search container, Emergency panel, Data grid, Collapsible dropdowns, and Results viewport).
  * Encapsulates inline JavaScript specifically for performance-critical functions such as search debounce and local pre-caching.
* **Imports Utilized**: `static/style.css`, `static/enhanced-features.js`.

### `config.py`
* **Classification**: Helper File
* **Purpose**: Centralized application configuration parser.
* **Responsibilities**: Parses environmental keys from `.env` or the underlying system environment, injecting standard fallback defaults for development scenarios.

### `utils.py`
* **Classification**: Helper File
* **Purpose**: Defines security and file validation utilities.
* **Responsibilities**: Validates uploaded file suffixes and executes binary magic header inspections to prevent malicious payload execution.
* **Major Functions**:
  * `allowed_file()`: Evaluates provided file extensions against an allowed list.
  * `validate_pdf_file()`: Inspects file streams for mandatory magic bytes (must commence with `%PDF`).

### `logger_config.py`
* **Classification**: Helper File
* **Purpose**: Establishes standard logger configuration.
* **Responsibilities**: Exposes pre-formatted, unified console logger instances across all application modules.

### `static/service-worker.js`
* **Classification**: Helper File
* **Purpose**: Controls the Progressive Web App (PWA) offline caching layer.
* **Responsibilities**: Intercepts DOM network fetches, serves assets locally when disconnected, and synchronizes static templates and manifests within the Cache Storage API.

### `scripts/generate_audio.py`
* **Classification**: Helper File
* **Purpose**: CLI script for bulk TTS pre-rendering.
* **Responsibilities**: Iterates programmatically over all scheme definitions ingested by `app.py`, sequentially invoking the audio service to pre-generate MP3 summaries.
* **Imports Utilized**: `app.py`, `services/audio_service.py`.
