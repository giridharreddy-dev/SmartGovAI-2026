# SmartGovAI

[![pytest](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml/badge.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026/actions/workflows/pytest.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Coverage](https://img.shields.io/badge/coverage-78%25-green.svg)](https://github.com/giridharreddy-dev/SmartGovAI-2026)

## Overview

SmartGovAI is an offline-first Progressive Web Application (PWA) supported by a Python Flask backend. It is designed as an academic prototype to explore mitigating the digital divide by helping citizens discover, evaluate eligibility for, and comprehend government health and welfare schemes through an accessible, language-first interface.

## Why This Project Exists

Rural citizens in India, particularly those with limited literacy and digital exposure, face significant barriers when attempting to access government welfare programs. Key issues include:
- **Language Barriers:** Information is often available in complex language or English.
- **Digital Literacy:** Many centralized portals require advanced digital navigation skills.
- **Connectivity:** Low-bandwidth or intermittent internet access hinders web portal usage.
- **Complexity:** Navigating eligibility requirements and required documents is difficult without assistance.

This project investigates how a combination of a Telugu-first UI, offline caching, and optional AI simplification could address these barriers.

## Who It Is For

The application is built with the following target audiences in mind (note: real-world adoption is proposed but not yet validated):
- Rural citizens in Andhra Pradesh
- Telugu-speaking users
- Users with limited digital literacy
- Family members or caregivers assisting citizens
- Community health workers (e.g., ASHAs)
- NGOs and community organizations

## What We Have Built

| Feature | Status | Evidence/Description |
|---|---|---|
| Telugu-first Interface | **IMPLEMENTED** | UI defaults to Telugu with English toggle. Tested via `test_localization.py`. |
| Offline PWA Cache | **IMPLEMENTED** | Service Worker caches scheme data, audio files, and UI assets for offline use. |
| Scheme Catalog | **IMPLEMENTED** | Centralized local JSON database (`data/`). |
| RAG AI Chat | **IMPLEMENTED** | Gemini API answers questions grounded in scheme catalog (requires internet). |
| PDF Simplification | **IMPLEMENTED** | Parses uploaded PDFs (with OCR fallback) and simplifies text via Gemini (requires internet). |
| Healthcare Facility Locator | **IMPLEMENTED** | Local `facilities.json` with Leaflet.js map and Haversine distance logic. |
| Deterministic Audio (TTS) | **IMPLEMENTED** | Pre-generated audio MP3s cached to avoid runtime TTS failures. |
| Document Checklist | **IMPLEMENTED** | Local evaluation logic renders checklist based on user inputs. |
| Analytics Dashboard | **PROTOTYPE** | `/analytics` route with SQLite backend, functional but requires scaling for production. |
| Security Features | **IMPLEMENTED** | CSRF protection, CSP nonces, strict headers, and Flask-Limiter. |
| Real-World Field Pilot | **PROPOSED** | Not yet deployed or validated with actual rural users. |

## Why It Is Different

The project combines several approaches to improve accessibility:
- **Telugu-first UX:** Prioritizes the regional language instead of treating it as an afterthought.
- **Offline-first Architecture:** Navigating the catalog, checking eligibility, and listening to pre-cached audio works without an internet connection.
- **AI Assistance:** Optional Gemini integration helps simplify complex policy PDFs and answer questions, falling back to local search if offline.
- **Privacy-Aware Design:** Core features (eligibility checking, checklists) process data entirely within the browser's `localStorage` without sending PII to the server.

## Architecture

SmartGovAI uses a decoupled client-server architecture:
- **Client-Side:** HTML5, Vanilla CSS3, ES6+ JavaScript (`enhanced-features.js`), Service Worker, `localStorage`.
- **Server-Side:** Python 3.10+ with Flask, SQLite (`feedback.db`), `pdfplumber`/Tesseract for parsing, Google Gemini API for AI features.

## AI Safety / Responsible AI

- **Grounding:** The `/chat` endpoint restricts Gemini to use only the provided scheme context.
- **Limitations:** AI is prone to hallucination. The system is NOT hallucination-proof. Users must verify final eligibility with official government sources.
- **Fallback Behavior:** If Gemini is unavailable, unconfigured, or offline, the app gracefully degrades to a deterministic local catalog search.

## Privacy and Security

- **Client-Side Processing:** No Personally Identifiable Information (PII) is sent to the server for eligibility checks.
- **Security Mechanisms:** Implements CSRF protection, Content Security Policy (CSP), rate-limiting (via Flask-Limiter), and robust file validation (magic bytes checking for PDFs).

## Offline Capability

**What works offline:**
- Viewing the scheme catalog and details.
- Checking basic eligibility.
- Viewing document checklists.
- Playing pre-cached audio descriptions.
- Healthcare facility lookup (map tiles may not load, but data and distances work).

**What requires internet:**
- The AI Chat Assistant (Gemini API).
- Uploading and simplifying new PDFs.
- Live map tile rendering.

## Current Limitations

- **No Official Government Tie-in:** This is an independent tool and cannot guarantee eligibility or grant benefits.
- **AI Dependency:** Advanced simplification relies on Google Gemini; if the API is down or unavailable, features degrade.
- **Static Facilities Data:** The `facilities.json` file is static and must be manually updated.

## What Still Needs Validation

- **Real Rural User Testing:** The UI's effectiveness for citizens with low digital literacy has not been measured in the field.
- **AI Accuracy Evaluation:** The accuracy of the Telugu simplification and RAG responses requires formal evaluation.
- **Data Freshness:** Establishing a pipeline to automatically update schemes when government policy changes.

## Testing

The project is thoroughly tested using `pytest`.
- **Current Result:** 78/78 tests pass.
- **Coverage:** ~78% scoped test coverage across backend services.

## Installation / Running

1. Clone the repository: `git clone https://github.com/giridharreddy-dev/SmartGovAI-2026.git`
2. Run setup: `setup.bat` (Windows) or `./setup.sh` (macOS/Linux).
3. Configure `.env` (copy from `.env.example`, set `SECRET_KEY`).
4. Activate virtual environment and run: `python app.py`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

SmartGovAI is an independent information tool and academic project. It is not an official government authority. Eligibility determinations made by this application are informational only.