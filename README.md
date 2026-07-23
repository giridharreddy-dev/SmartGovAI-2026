# SmartGovAI

[![pytest](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml/badge.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-86%25-green.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)

## Table of Contents
1. [Abstract/Overview](#abstractoverview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Tech Stack](#tech-stack)
5. [Features](#features)
6. [System Setup/Installation](#system-setupinstallation)
7. [Team & Faculty Guide](#team--faculty-guide)
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

### Server-Side
* **Framework:** Python 3.10+ with Flask
* **Database:** SQLite (`feedback.db`)
* **File Parsing:** `pdfplumber` with Tesseract OCR fallback
* **Audio Generation:** gTTS (Google Text-to-Speech)
* **Artificial Intelligence:** Google Gemini API
* **Security & Rate Limiting:** Flask-Limiter, Redis, Flask-WTF

---

## Features

* **Modular Scheme Loading:** During application startup, the server dynamically scans the `data/` directory, validates JSON entries against structural schema constraints, and merges valid schemes into a single in-memory catalog.
* **Artificial Intelligence Simplification:** Extends Google Gemini API to parse complex policy documents, extracting relevant eligibility and benefit criteria and translating them into simple Telugu.
* **Deterministic Audio Caching:** Pre-renders audio MP3 assets for all schemes. It only initiates an external Text-to-Speech call when a cache miss occurs, conserving bandwidth and ensuring immediate availability.
* **Enterprise-Grade Security:** Implements Cross-Site Request Forgery (CSRF) protection, Content Security Policy (CSP) headers, strict HTTP headers, and robust file upload validation (including magic byte verification).
* **Resilient Rate Limiting:** Utilizes an in-memory tracking fallback mechanism if the primary Redis server becomes unavailable, guaranteeing continuous availability.

---

## System Setup/Installation

### Prerequisites
* Python 3.10+
* `pip` and `virtualenv`
* *Optional:* Tesseract-OCR and Poppler binaries installed on the system path for advanced PDF parsing.

### Environment Configuration

Configure the required parameters by adding them to the local `.env` file:

```bash
# Flask Session Encryption Key (Required in production)
SECRET_KEY=your-production-secret-key-here

# Optional: Google Gemini API Key (Enables PDF simplification upload feature)
GEMINI_API_KEY=<YOUR_API_KEY>

# Optional: SQLite Database Path (Defaults to feedback.db)
DB_PATH=feedback.db

# Optional: Redis URL for Rate Limit Storage
REDIS_URL=redis://localhost:6379

# Configure API Rate limits
RATELIMIT_DEFAULT="200 per day; 50 per hour"
RATELIMIT_SIMPLIFY="10 per minute; 60 per hour"
RATELIMIT_FEEDBACK="20 per minute"
RATELIMIT_REPORT="10 per minute"
```

### Installation Steps

1. Clone the repository and navigate to the directory:
   ```bash
   git clone https://github.com/giridharreddy-dev/SmartGovAI-2026.git
   cd SmartGovAI-2026
   ```

2. Establish and activate the virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate       # Windows PowerShell
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Pre-generate the audio files:
   ```bash
   python -m scripts.generate_audio
   ```

5. Launch the application server:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://localhost:5000`.

### Testing
To execute the automated test suite and review code coverage:
```bash
pytest
```

---

## Team & Faculty Guide

* **Development Team:** [Student Names]
* **Faculty Guide:** [Faculty Guide Name]

---

## Future Scope

Subsequent iterations of the SmartGovAI system may address the following objectives:
* **Asynchronous Processing:** Transitioning AI simplification and audio generation tasks to an asynchronous message queue (e.g., Celery) to prevent thread blocking under high concurrent loads.
* **Modular Refactoring:** Restructuring the monolithic routing file into Flask Blueprints to isolate responsibilities and improve maintainability as the application scales.
* **Expanded Linguistic Support:** Extending the translation and text-to-speech architecture to accommodate additional regional languages to broaden accessibility across different states.
* **Infrastructure Automation:** Introducing Docker and continuous integration/continuous deployment (CI/CD) pipelines to standardize production environments.