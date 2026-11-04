"""Static React shell and public, offline-safe data for Citizen Studio."""

import json
from pathlib import Path

from flask import Blueprint, Response, abort, current_app, jsonify, request, send_from_directory, url_for
from flask_wtf.csrf import generate_csrf

from services.studio_narration import STUDIO_VOICES, studio_audio_asset
from services.scheme_revisions import checklist, section_statuses
from services.studio_search import SearchUnavailable, model_directory, search_corpus, semantic_ids
from utils import safe_url


def _sections(value):
    value = value if isinstance(value, dict) else {}
    return {
        key: value[key]
        for key in ("description", "eligibility", "benefits", "documents", "steps")
        if isinstance(value.get(key), str) and value[key].strip()
    }


def _scheme(name, scheme, root):
    checklist_items, checklist_aliases = checklist(scheme)
    documents = [
        {"en": item, "te": "", "optional": False}
        if isinstance(item, str)
        else {"en": item["name"], "te": item.get("name_te", ""), "optional": item.get("optional") is True}
        for item in (scheme.get("required_documents") or [])
        if isinstance(item, str) or (isinstance(item, dict) and item.get("name"))
    ]
    questions = [
        {"en": item.get("question_en", ""), "te": item.get("question_te", "")}
        for item in (scheme.get("eligibility_questions") or [])
        if isinstance(item, dict) and (item.get("question_en") or item.get("question_te"))
    ]
    audio = scheme.get("audio_file") or ""
    audio_url = None
    if audio.startswith("static/audio/"):
        audio_dir = (root / "static" / "audio").resolve()
        candidate = (root / audio).resolve()
        if candidate.is_relative_to(audio_dir) and candidate.is_file():
            audio_url = url_for("static", filename=candidate.relative_to(root / "static").as_posix())
    recordings = {}
    for language in STUDIO_VOICES:
        asset = studio_audio_asset(scheme["slug"], language)
        file = root / "static" / asset
        try:
            info = file.stat()
        except FileNotFoundError:
            continue
        if info.st_size >= 1024 and file.is_file():
            recordings[language] = url_for("static", filename=asset.as_posix(), v=f"{info.st_mtime_ns:x}")
    return {
        "id": scheme["slug"],
        "name": name,
        "nameTe": scheme.get("telugu_name"),
        "region": scheme.get("level") or "",
        "category": scheme.get("category") or "",
        "sector": scheme.get("sector") or "health",
        "keywords": scheme.get("keywords") or [],
        "aliases": scheme.get("aliases") or [],
        "programme_components": scheme.get("programme_components") or [],
        "en": _sections(scheme.get("simplified")),
        "te": _sections(scheme.get("telugu")),
        "source": {
            "label": scheme.get("source_name"),
            "url": safe_url(scheme.get("official_website")) or safe_url(scheme.get("source_url")) or "",
            "updated": scheme.get("last_updated") or "",
            "reviewed": scheme.get("source_reviewed") or "",
        },
        "documents": documents,
        "operations": scheme.get("operations") if scheme.get("operations_reviewed") else None,
        "section_statuses": section_statuses(scheme),
        "checklist": checklist_items,
        "checklist_aliases": checklist_aliases,
        "operations_source": scheme.get("operations_source"),
        "questions": questions,
        "audio": audio_url,
        "audioLanguage": scheme.get("audio_language", "te"),
        "recordings": recordings,
        "directoryEntry": bool(scheme.get("directory_entry")),
    }


def _public_json(data):
    response = Response(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), mimetype="application/json"
    )
    response.cache_control.public = True
    response.cache_control.max_age = 300
    response.add_etag()
    return response.make_conditional(request)


def make_studio(root, schemes, facilities):
    studio = Blueprint("studio", __name__, url_prefix="/studio")
    root = Path(root)
    dist = root / "frontend" / "dist"
    passages, fingerprint = search_corpus(schemes)

    @studio.get("/")
    def index():
        if not (dist / "index.html").is_file():
            abort(404)
        response = send_from_directory(dist, "index.html", max_age=0)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
            "font-src 'self'; media-src 'self'; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    @studio.get("/assets/<path:name>")
    def assets(name):
        return send_from_directory(dist / "assets", name, max_age=31536000)

    @studio.get('/<any("sw.js","manifest.webmanifest","mark.svg","font-licenses.txt"):name>')
    def shell_asset(name):
        return send_from_directory(dist, name, max_age=0)

    @studio.get("/catalog.json")
    def catalog():
        return _public_json({"schemes": [_scheme(name, item, root) for name, item in schemes.items()]})

    @studio.post("/search")
    def search():
        data = request.get_json(silent=True)
        query = data.get("query") if isinstance(data, dict) else None
        if not isinstance(query, str) or not query.strip() or len(query) > 500:
            return jsonify(error="A search query of up to 500 characters is required."), 400
        region, sector = data.get("region", ""), data.get("sector", "")
        if not all(isinstance(value, str) and len(value) <= 100 for value in (region, sector)):
            return jsonify(error="Invalid search filters."), 400
        allowed = {
            item["slug"] for item in schemes.values()
            if (not region or item.get("level") == region)
            and (not sector or (item.get("sector") or "health") == sector)
        }
        try:
            ids = semantic_ids(model_directory(root), passages, fingerprint, query.strip(), allowed)
            response = jsonify(ids=ids)
        except SearchUnavailable:
            response = jsonify(error="Semantic search is currently unavailable.")
            response.status_code = 503
        except Exception:
            current_app.logger.exception("Citizen Studio semantic search failed")
            response = jsonify(error="Semantic search is currently unavailable.")
            response.status_code = 503
        response.cache_control.no_store = True
        return response

    @studio.get("/facilities.json")
    def directory():
        keys = ("id", "name", "type", "district", "mandal", "village", "contact", "lat", "lng")
        return _public_json({"facilities": [{key: item.get(key) for key in keys} for item in facilities]})

    @studio.get("/session")
    def session_token():
        response = jsonify(csrfToken=generate_csrf())
        response.headers["Cache-Control"] = "no-store"
        return response

    return studio
