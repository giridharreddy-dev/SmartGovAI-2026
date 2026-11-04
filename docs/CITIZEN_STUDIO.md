# Citizen Studio

Citizen Studio continues SmartGovAI-2026 and uses the Google Studio V2 project as a reference for its portal workflows. The server remains Python and Flask. The citizen interface is built with HTML, CSS, JavaScript and React; Node.js and Vite build the assets and are not required by the running Flask server. The classic interface, legacy APIs and analytics remain available.

## Run on Windows

Use Python 3.12 and Node.js 22.12+ (CI uses Node 24). Run these commands from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
$env:SECRET_KEY = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
.\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:5000 --threads=6 app:app
```

Open `http://127.0.0.1:5000/`. The server starts with a local catalog when no Gemini key is configured. Supply `GEMINI_API_KEY` and, if needed, `GEMINI_MODEL_NAME` through the process environment or a private `.env` file. Use the same secret across production workers and restarts. Use `npm --prefix frontend test` and `.\.venv\Scripts\python.exe -m pytest` for the automated suites.

## Citizen workflows and data

- The health catalog and facility directory come from the original repository datasets. A source link or catalog date is not a guarantee that a scheme is current. Missing translations fall back to existing catalog text. No scheme eligibility or benefit is decided by this portal.
- The expanded directory in `data/studio/welfare.json` includes brief, independently written English and Telugu summaries linked to government sources. The review date is when the source was checked. Keep IDs stable, verify replacements against the administering agency, and keep official titles as published. Directory entries point to the source for current eligibility, required documents, and application steps.
- The [official myScheme search](https://www.myscheme.gov.in/search) provides wider central and state coverage online. Its [terms](https://www.myscheme.gov.in/terms-of-use) require written authorization for scraping. The local catalog is a subset.
- Bookmarks, comparisons, document checks and eligibility answers are stored in this browser. The self-check records answers and links to the scheme's source; it does not assign a score or submit an application. These records are separate from the classic portal's browser storage.
- Once “Offline copy ready” appears, the Studio shell, local search, comparison, checklists, printable guides and facility directory can work offline. External sources, map links, fresh AI responses and audio that has not been cached need a connection.
- Local assistant search sends no query to Flask. The explicit online action posts a question to Flask and may send it to Gemini. PDF uploads require consent, use Flask's PDF validation and optionally OCR, and send extracted text to Gemini when configured. The temporary PDF is removed after processing; PDF summary narration uses only the local browser voice. Do not submit private documents. For PDF guides, choose **Print / save PDF**, then **Save as PDF** in the browser dialog.

## Generate scheme narration

The **Listen** button uses a generated MP3 in the selected language when it is available. Microsoft Shruti reads the Telugu summary and Microsoft Neerja reads the English summary. A recording played online can be replayed offline while it remains in the browser cache. If a recording is missing or fails to load, Studio tries an installed local voice in the same language.

Run the generator from the repository root after installing the Python requirements:

```powershell
.\.venv\Scripts\python.exe -m scripts.generate_audio --studio
.\.venv\Scripts\python.exe -m scripts.generate_audio --studio --scheme welfare-pm-kisan --language te
```

The script writes to `static/audio/studio/bilingual/` and skips valid MP3s on subsequent runs. A narration ZIP containing that directory can also be extracted at the repository root. The recordings are excluded from Git. The default Edge provider is for local previews. Before publishing recordings, use a provider and account that allow the intended distribution. For an authorized Azure Speech resource, set `SPEECH_KEY` and `SPEECH_REGION` privately and pass `--provider azure --overwrite` to regenerate any local Edge clips with Azure.

## Deployment and verification

`docker compose up --build` builds React in a separate stage and serves it through non-root Gunicorn workers. The compose service stores feedback in a named volume. It does not migrate a previous host-side SQLite file; back up and migrate existing data deliberately before switching. Set a shared `REDIS_URL` before running multiple workers with a shared rate limit. Put the app behind HTTPS, set `SESSION_COOKIE_SECURE=1` and the correct `TRUSTED_PROXIES`, and enforce request size and concurrency limits at the proxy. Restrict direct access to Gunicorn. Review sessions, backup and restore, and worker capacity in the real deployment. Use `/healthz` and `/readyz` for monitoring and readiness.

The main app falls back to the classic portal if the React build is absent. Studio is served under `/studio/`, so its service worker only owns that scope and caches only public read-only data and build files. A worker update activates when the previous Studio tabs close. No live provider, field pilot, or production rollout is implied by a successful local run.
