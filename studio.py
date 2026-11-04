"""Static React shell and public, offline-safe data for Citizen Studio."""

import json
from pathlib import Path

from flask import Blueprint, Response, abort, jsonify, request, send_from_directory, url_for
from flask_wtf.csrf import generate_csrf

from utils import safe_url


def _sections(value):
    value = value if isinstance(value, dict) else {}
    return {
        key: value[key]
        for key in ("description", "eligibility", "benefits", "documents", "steps")
        if isinstance(value.get(key), str) and value[key].strip()
    }


def _scheme(name, scheme, root):
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
    return {
        "id": scheme["slug"],
        "name": name,
        "nameTe": scheme.get("telugu_name"),
        "region": scheme.get("level") or "",
        "category": scheme.get("category") or "",
        "keywords": scheme.get("keywords") or [],
        "en": _sections(scheme.get("simplified")),
        "te": _sections(scheme.get("telugu")),
        "source": {
            "label": scheme.get("source_name"),
            "url": safe_url(scheme.get("official_website")) or safe_url(scheme.get("source_url")) or "",
            "updated": scheme.get("last_updated") or "",
        },
        "documents": documents,
        "questions": questions,
        "audio": audio_url,
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
