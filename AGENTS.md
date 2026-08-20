# Autonomous AI Coding Agent Guidelines

This document outlines the operational boundaries, architectural constraints, and safety protocols for any AI coding agents (such as GitHub Copilot Workspace, Gemini, or Claude) interacting with the SmartGovAI repository.

## 1. Core Architectural Invariants
When modifying this codebase, agents **must preserve** the following invariants:

- **Offline-First Architecture**: The application must function without an internet connection. Do not introduce dependencies on external CDNs or APIs for critical rendering paths. Ensure Service Worker (`static/service-worker.js`) rules are updated if static assets change.
- **Telugu-First Accessibility**: The primary language of the application is Telugu. UI elements must default to Telugu, and any new features must include bilingual support (Telugu and English).
- **Client-Side Eligibility Data**: Eligibility evaluations, form completions, and document checklists must remain within the browser's `localStorage` and must not be sent to the server. (A tested server-side `/eligibility-check` endpoint exists but is intentionally not called by the frontend — don't wire it up without updating this note and the README's Security & Privacy section.)
- **Synchronous Fallbacks**: If AI services (e.g., Gemini API) or Text-to-Speech generation fail, the application must gracefully degrade to basic catalog search and local browser Text-to-Speech without crashing.

## 2. Refactoring Boundaries
- **No Unprompted Refactoring**: Do not autonomously refactor application logic, rename Python functions/classes, change Flask routes, alter database schemas, or modify the `.venv` setup unless explicitly directed by the user.
- **Preserve Documentation & Structure**: The repository uses `docs/` for documentation, `scripts/` for utilities, `services/` for core logic, and `static/`/`templates/` for the frontend. Do not blindly delete files that appear unusual. Check `docs/` and historical documentation before assuming a file is obsolete.
- **Test Fidelity**: Any modifications must not decrease the existing test coverage. The number of passed tests in `pytest` must remain stable or increase. No new test failures are acceptable.

## 3. Localization and Generation Rules
- **No Translation Hallucinations**: Do not invent or guess Telugu translations for official scheme names or technical errors. Rely on provided translation dictionaries or authoritative sources.
- **Audio Pre-caching**: Ensure that newly added schemes generate corresponding high-fidelity MP3s using the `scripts/generate_audio.py` pipeline.

## 4. Setup and Environment
- **Virtual Environment**: The project explicitly uses `.venv` for its Python virtual environment (not `venv`, `myenv`, or `env`). Setup scripts (`setup.bat`, `setup.sh`) depend on this naming convention.
- **Secrets Management**: Never print, log, or commit actual secret values. Use `.env.example` as the reference for environment variables.

By strictly adhering to these guidelines, agents will maintain the safety, accessibility, and offline resilience that are critical to the SmartGovAI mission.
