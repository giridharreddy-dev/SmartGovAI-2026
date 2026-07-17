# SmartGov Health: File Dictionary

This document details the purpose, responsibilities, API signatures, dependencies, and classifications of every important file in the SmartGov Health codebase.

---

## 1. Summary Directory Table

| File Name | Architecture Type | Primary Purpose | Key Dependencies (Imports) | Imported By |
| :--- | :--- | :--- | :--- | :--- |
| **[app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py)** | Core File | Main controller & route dispatcher | `config`, `database`, `utils`, `gemini_service`, `pdf_service`, `audio_service`, `logger_config` | `tests/test_app.py` |
| **[database.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/database.py)** | Core File | Database persistence (SQLite) | `logger_config` | `app.py`, `tests/test_app.py` |
| **[services/audio_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/audio_service.py)** | Core File | Telugu TTS generator (gTTS) | None | `app.py`, `generate_audio.py`, `tests/test_audio_service.py` |
| **[services/gemini_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/gemini_service.py)** | Core File | AI Policy simplification | `config` | `app.py`, `tests/test_gemini_service.py` |
| **[services/pdf_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/pdf_service.py)** | Core File | PDF character extraction & OCR | `config` | `app.py`, `tests/test_pdf_service.py` |
| **[static/enhanced-features.js](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/static/enhanced-features.js)** | Core File | Browser UI actions & storage caching | None | `templates/index.html` |
| **[templates/index.html](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/templates/index.html)** | Core File | PWA application markup | `style.css`, `enhanced-features.js` | None (served by `app.py`) |
| **[config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/config.py)** | Helper File | Parses app configuration | None | `app.py`, `gemini_service.py`, `pdf_service.py` |
| **[utils.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/utils.py)** | Helper File | Upload file verification | None | `app.py`, `tests/test_utils.py` |
| **[logger_config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/logger_config.py)** | Helper File | Formats logging instances | None | `app.py`, `database.py` |
| **[static/service-worker.js](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/static/service-worker.js)** | Helper File | Offline PWA caching | None | `enhanced-features.js` (registration) |
| **[scripts/generate_audio.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/scripts/generate_audio.py)** | Helper File | Offline bulk TTS pre-rendering script | `app`, `audio_service` | None |

---

## 2. File-by-File Technical Review

### 📄 `app.py`
* **Classification**: Core File
* **Purpose**: Serves as the main entry point and web controller routing traffic for the application.
* **Responsibilities**:
  * Initializes the Flask app context, CSRF token verification middleware (`Flask-WTF`), log configurations, and client rate limits (`Flask-Limiter`).
  * Dynamically scans, checks, and loads all `.json` files inside the `data/` directory at startup.
  * Exposes HTTP endpoints for rendering the UI, simplifying PDFs, logging ratings, and serving audio files.
* **Major Functions**:
  * `load_schemes()`: Merges all files in `data/` into a single memory dictionary.
  * `index()`: Standard HTML renderer for `/`.
  * `simplify()`: API `/simplify` POST handler processing text/file simplification.
  * `feedback_route()`: API `/feedback` POST handler registering client feedback ratings.
* **Which Files Import It**: None directly (executed as a runtime entry point; imported in `tests/test_app.py` and `scripts/generate_audio.py`).
* **Which Files It Imports**: [config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/config.py), [database.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/database.py), [utils.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/utils.py), [services/gemini_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/gemini_service.py), [services/pdf_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/pdf_service.py), [services/audio_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/audio_service.py), [logger_config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/logger_config.py).

### 📄 `database.py`
* **Classification**: Core File
* **Purpose**: Local data persistence manager.
* **Responsibilities**:
  * Creates and maintains SQLite databases (`feedback.db`).
  * Creates tables: `requests` (simplification requests), `feedback` (user ratings), and `audit_logs` (security events and exceptions).
  * Manages thread-safe SQLite connection contexts.
* **Major Functions**:
  * `init_db()`: Boots database tables.
  * `log_request()`: Logs request metadata and duration audit data.
  * `save_feedback()`: Connects and inserts user feedback ratings.
  * `log_audit()`: Formats and stores audit log entries.
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [tests/test_app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/tests/test_app.py).
* **Which Files It Imports**: [logger_config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/logger_config.py).

### 📄 `services/audio_service.py`
* **Classification**: Core File
* **Purpose**: Coordinates Telugu Text-to-Speech (TTS) generation.
* **Responsibilities**:
  * Converts plain text welfares into audio summaries using the `gTTS` library.
  * Implements query sleep throttles and connection retry buffers.
  * Skips rendering if the requested summary already exists in the static cache.
  * Maintains disk footprint limits by deleting old cached audio files.
* **Major Functions**:
  * `generate_audio_file()`: Fetches TTS streams and handles connection error retries.
  * `cleanup_old_audio()`: Rotates the audio directory to prevent storage overflows.
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [scripts/generate_audio.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/scripts/generate_audio.py), [tests/test_audio_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/tests/test_audio_service.py).
* **Which Files It Imports**: None.

### 📄 `services/gemini_service.py`
* **Classification**: Core File
* **Purpose**: Connects with Google Gemini AI models for translation and policy simplification.
* **Responsibilities**:
  * Assembles system instructions requesting Gemini to output clean JSON schemas.
  * Translates policy structures between English and simple Telugu.
* **Major Functions**:
  * `simplify_policy_text()`: Interfaces with Gemini's SDK, validating structures.
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [tests/test_gemini_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/tests/test_gemini_service.py).
* **Which Files It Imports**: [config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/config.py).

### 📄 `services/pdf_service.py`
* **Classification**: Core File
* **Purpose**: Document content extractor.
* **Responsibilities**:
  * Reads and extracts textual characters from PDF attachments.
  * Falls back to Gemini vision models (OCR mode) when direct text extraction fails (e.g. scanned image PDFs).
* **Major Functions**:
  * `extract_text_from_pdf()`: Direct character reading.
  * `perform_ocr_on_pdf()`: Visual layout rendering and OCR parsing via Gemini.
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [tests/test_pdf_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/tests/test_pdf_service.py).
* **Which Files It Imports**: [config.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/config.py).

### 📄 `static/enhanced-features.js`
* **Classification**: Core File
* **Purpose**: Drives client-side interface actions.
* **Responsibilities**:
  * Intercepts browser actions to display offline flags.
  * Implements dynamic forms for feedback and reports.
  * Renders eligibility question forms and saves user checklist states in `localStorage`.
  * Protects AJAX POST requests by forwarding CSRF validation headers.
* **Major Namespaces**:
  * `SmartGovEnhanced`: Namespace holding all UI initialization and event handlers.
* **Which Files Import It**: [templates/index.html](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/templates/index.html).
* **Which Files It Imports**: None.

### 📄 `templates/index.html`
* **Classification**: Core File
* **Purpose**: Primary user interface.
* **Responsibilities**:
  * Provides the structural layout (Search, Emergency panel, cards list grid, collapsible tools dropdown, and results display block).
  * Houses inline JavaScript for performance functions like fuzzy search pre-caching and debouncing.
* **Which Files Import It**: None (served by `app.py`).
* **Which Files It Imports**: [static/style.css](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/static/style.css), [static/enhanced-features.js](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/static/enhanced-features.js).

### 📄 `config.py`
* **Classification**: Helper File
* **Purpose**: Application configuration.
* **Responsibilities**: Parses environmental keys from `.env` or system environments, supplying standard defaults for development.
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [services/gemini_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/gemini_service.py), [services/pdf_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/pdf_service.py).
* **Which Files It Imports**: None.

### 📄 `utils.py`
* **Classification**: Helper File
* **Purpose**: Security validation utilities.
* **Responsibilities**: Validates file suffixes and examines binary magic headers to prevent malicious file uploads.
* **Major Functions**:
  * `allowed_file()`: Evaluates file extensions.
  * `validate_pdf_file()`: Inspects magic bytes (must begin with `%PDF`).
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [tests/test_utils.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/tests/test_utils.py).
* **Which Files It Imports**: None.

### 📄 `logger_config.py`
* **Classification**: Helper File
* **Purpose**: Logger standardization.
* **Responsibilities**: Provides pre-formatted, unified console logger instances.
* **Which Files Import It**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [database.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/database.py).
* **Which Files It Imports**: None.

### 📄 `static/service-worker.js`
* **Classification**: Helper File
* **Purpose**: Offline PWA caching.
* **Responsibilities**: Intercepts request fetches, serves files locally when offline, and maintains static templates and manifests in cache storage.
* **Which Files Import It**: None (registered by browser).
* **Which Files It Imports**: None.

### 📄 `scripts/generate_audio.py`
* **Classification**: Helper File
* **Purpose**: Offline bulk TTS pre-rendering script.
* **Responsibilities**: Iterates over all schemes loaded by `app.py`, calling the audio service to pre-generate MP3 summaries.
* **Which Files Import It**: None.
* **Which Files It Imports**: [app.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/app.py), [services/audio_service.py](file:///c:/Users/HP/OneDrive/Desktop/SmartGovAI-2026/services/audio_service.py).
