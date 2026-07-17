"""Flask application for SmartGovAI scheme lookup, simplification, and feedback APIs."""

import json
import os
import sqlite3
import time
import urllib.parse
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict

from flask import Flask, g, jsonify, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

import database
from config import (
    AUDIO_DIR,
    BASE_DIR,
    DB_PATH,
    DEBUG_MODE,
    MAX_UPLOAD_SIZE,
    SCHEMES_DIR,
    SERVER_HOST,
    SERVER_PORT,
    UPLOAD_DIR,
)
from logger_config import logger
from services.audio_service import generate_telugu_audio
from services.gemini_service import is_gemini_available, simplify_document
from services.pdf_service import extract_text_with_ocr_fallback, is_ocr_available
from utils import allowed_file

app = Flask(__name__)

# Configure CSRF protection
csrf = CSRFProtect(app)

# Disable CSRF and Rate Limiting when running tests
if app.config.get("TESTING") or os.environ.get("TESTING") == "true":
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["RATELIMIT_ENABLED"] = False

# Configure Rate Limiting
redis_url = os.environ.get("REDIS_URL", "").strip()
if redis_url:
    storage_uri = f"{redis_url},memory://"
else:
    storage_uri = "memory://"

default_limit = os.environ.get("RATELIMIT_DEFAULT", "200 per day; 50 per hour")
simplify_limit = os.environ.get("RATELIMIT_SIMPLIFY", "10 per minute; 60 per hour")
feedback_limit = os.environ.get("RATELIMIT_FEEDBACK", "20 per minute")
report_limit = os.environ.get("RATELIMIT_REPORT", "10 per minute")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[default_limit],
    storage_uri=storage_uri,
    strategy="fixed-window"
)


@app.before_request
def log_request_start() -> None:
    """Record the start of an incoming request for logging and tracing."""
    g.request_start_time = time.perf_counter()
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logger.info(
        "Request received: method='%s' endpoint='%s' client_ip='%s'",
        request.method,
        request.endpoint or request.path,
        client_ip,
    )


@app.after_request
def log_request_end(response):
    """Log request completion and add basic security headers to the response."""
    duration = time.perf_counter() - getattr(g, "request_start_time", time.perf_counter())
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logger.info(
        "Request completed: method='%s' endpoint='%s' status=%s client_ip='%s' duration=%.3f sec",
        request.method,
        request.endpoint or request.path,
        response.status_code,
        client_ip,
        duration,
    )
    
    # Add strict but compatible security headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=()")
    
    # Basic CSP compatible with external Google Fonts and inline scripts used in templates
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "img-src 'self' data:;"
    )
    response.headers.setdefault("Content-Security-Policy", csp_policy)
    return response


# Feature status logging (no secrets)
logger.info(
    "Startup: Gemini AI %s",
    "enabled" if is_gemini_available() else "disabled",
)
logger.info(
    "Startup: OCR support %s",
    "available" if is_ocr_available() else "not installed",
)

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
secret_key = os.environ.get("SECRET_KEY", "").strip()
if not secret_key:
    # Use a dummy secret key only if testing to allow tests to run
    if app.config.get("TESTING"):
        secret_key = "testing-secret-key"
    else:
        raise RuntimeError("SECRET_KEY is not set. Please add it to your .env file.")
app.secret_key = secret_key

database.init_db()
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_scheme(name: str, data: Dict[str, Any]) -> bool:
    """Validate required fields in the scheme data structure."""
    if not name or not isinstance(data, dict):
        return False
    
    required_top = ["category", "original_complex_text", "required_documents"]
    for field in required_top:
        if field not in data:
            logger.warning("Scheme '%s' validation failure: missing top-level field '%s'", name, field)
            return False
            
    simplified = data.get("simplified")
    if not isinstance(simplified, dict):
        logger.warning("Scheme '%s' validation failure: missing or invalid 'simplified' section", name)
        return False
    for field in ["eligibility", "benefits", "documents", "steps"]:
        if field not in simplified:
            logger.warning("Scheme '%s' validation failure: missing 'simplified.%s' field", name, field)
            return False
            
    telugu = data.get("telugu")
    if not isinstance(telugu, dict):
        logger.warning("Scheme '%s' validation failure: missing or invalid 'telugu' section", name)
        return False
    for field in ["eligibility", "benefits", "documents", "steps"]:
        if field not in telugu:
            logger.warning("Scheme '%s' validation failure: missing 'telugu.%s' field", name, field)
            return False
            
    return True


@lru_cache(maxsize=1)
def load_schemes() -> Dict[str, Any]:
    """Load and merge all valid scheme definitions from JSON files in the data directory."""
    merged_schemes = {}
    if not os.path.exists(SCHEMES_DIR):
        logger.warning("Schemes directory '%s' does not exist.", SCHEMES_DIR)
        return merged_schemes
        
    for filename in sorted(os.listdir(SCHEMES_DIR)):
        if filename.endswith(".json") and filename != "scheme_schema.json":
            filepath = os.path.join(SCHEMES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for scheme_name, scheme_data in data.items():
                        if validate_scheme(scheme_name, scheme_data):
                            merged_schemes[scheme_name] = scheme_data
                        else:
                            logger.warning("Skipping invalid scheme '%s' in file '%s'", scheme_name, filename)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed to load or parse scheme file '%s': %s", filename, e)
    return merged_schemes


# Load schemes safely
try:
    schemes = load_schemes()
    scheme_names = list(schemes.keys())
    logger.info("Startup: loaded %d valid schemes.", len(schemes))
except Exception:
    logger.exception("Failed to load schemes database.")
    raise

API_NAME = "SmartGovAI"
API_VERSION = "1.0.0"
API_DESCRIPTION = "SmartGovAI public API for scheme lookup and simplification."
STARTUP_TIME = datetime.utcnow()


def api_response(data: Dict[str, Any], status_code: int = 200) -> Any:
    """Wrap response data in the standard JSON envelope used by the API."""
    response = {
        "api_name": API_NAME,
        "api_version": API_VERSION,
        "api_description": API_DESCRIPTION,
        **data,
    }
    if "status" not in response:
        response["status"] = "success"
    return jsonify(response), status_code


def api_error(message: str, status_code: int = 400, error_code: str = None, details: Any = None) -> Any:
    """Build a consistent JSON error response for API failures."""
    payload = {
        "status": "error",
        "error": message,
    }
    if error_code:
        payload["error_code"] = error_code
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


def static_scheme_response(scheme_name: str, scheme_data: Dict[str, Any], request_id: int) -> Dict[str, Any]:
    """Construct a normalized response payload for a built-in scheme."""
    audio_rel_path = generate_telugu_audio(
        scheme_data["telugu"],
        scheme_name,
        scheme_data.get("audio_file"),
    )
    voice_url = url_for("static", filename=audio_rel_path) if audio_rel_path else None

    return {
        "request_id": request_id,
        "scheme_name": scheme_name,
        "level": scheme_data.get("level", ""),
        "category": scheme_data.get("category", ""),
        "source_name": scheme_data.get("source_name", "Official source"),
        "source_url": scheme_data.get("source_url", ""),
        "simplified": scheme_data["simplified"],
        "telugu": scheme_data["telugu"],
        "voice_url": voice_url,
    }


@app.errorhandler(413)
def too_large(_error) -> Any:
    """Return a JSON response when uploaded files exceed the max content size."""
    size_mb = MAX_UPLOAD_SIZE // (1024 * 1024)
    return api_error(
        f"File too large. Please upload a PDF below {size_mb} MB.",
        413,
        error_code="PAYLOAD_TOO_LARGE"
    )


@app.errorhandler(404)
def not_found(_error) -> Any:
    """Return a JSON response for missing endpoints, or HTML for browsers."""
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return api_error("Resource not found.", 404, error_code="NOT_FOUND")
    return render_template("offline.html"), 404


@app.errorhandler(500)
def internal_error(error) -> Any:
    """Return a JSON response for unhandled server errors."""
    logger.exception("Unhandled server error: %s", error)
    return api_error("An unexpected server error occurred.", 500, error_code="INTERNAL_SERVER_ERROR")


@app.errorhandler(Exception)
def handle_unexpected_exception(error) -> Any:
    """Catch and report unexpected exceptions."""
    logger.exception("Unhandled exception: %s", error)
    return api_error("An unexpected error occurred.", 500, error_code="UNHANDLED_EXCEPTION")


@app.route("/")
def index() -> Any:
    """Render the homepage with available schemes."""
    return render_template("index.html", schemes=schemes, scheme_names=scheme_names)


@app.route("/offline.html")
def offline() -> Any:
    """Render an offline fallback page."""
    return render_template("offline.html")


def build_health_status() -> Dict[str, Any]:
    """Collect health and availability details for monitoring endpoints."""
    checks = {
        "upload_dir": "ok" if os.path.exists(UPLOAD_DIR) and os.access(UPLOAD_DIR, os.W_OK) else "failed",
        "audio_dir": "ok" if os.path.exists(AUDIO_DIR) and os.access(AUDIO_DIR, os.W_OK) else "failed",
    }
    status = "ok" if checks["upload_dir"] == "ok" and checks["audio_dir"] == "ok" else "degraded"
    if status != "ok":
        logger.warning("Health check: directory accessibility issue.")
    return {
        "service": API_NAME,
        "status": status,
        "schemes": len(schemes),
        "gemini_pdf_support": is_gemini_available(),
        "checks": checks,
        "startup_time": STARTUP_TIME.isoformat() + "Z",
        "current_time": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": int((datetime.utcnow() - STARTUP_TIME).total_seconds()),
    }


@app.route("/healthz")
def healthz() -> Any:
    """Return a JSON health status for the service."""
    return api_response(build_health_status())


@app.route("/health")
def health() -> Any:
    """Alias for the health endpoint."""
    return api_response(build_health_status())


@app.route("/version")
def version() -> Any:
    """Return API version and metadata."""
    return api_response({
        "version": API_VERSION,
        "name": API_NAME,
        "description": API_DESCRIPTION,
        "startup_time": STARTUP_TIME.isoformat() + "Z",
    })


@app.route("/simplify", methods=["POST"])
@limiter.limit(simplify_limit)
def simplify() -> Any:
    """Accept a PDF upload, simplify it via Gemini, and return JSON results."""
    file = request.files.get("document")
    if file:
        valid, result = allowed_file(file)
        if not valid:
            logger.warning(
                "Rejected upload '%s': %s",
                file.filename,
                result,
            )
            return api_error(result, 400, error_code="INVALID_FILE_TYPE")

        safe_filename = result
        if not is_gemini_available():
            logger.error(
                "PDF simplification blocked: GEMINI_API_KEY is not configured",
            )
            return api_error(
                "PDF simplification is currently unavailable. Please try again later.",
                503,
                error_code="SERVICE_UNAVAILABLE"
            )

        # Ensure uploaded file begins with PDF header bytes before saving to disk.
        header = file.read(4)
        file.seek(0)
        
        if not header.startswith(b"%PDF"):
            logger.warning("Rejected upload: not a valid PDF according to header check: %s", safe_filename)
            return api_error("Uploaded file is not a valid PDF.", 400, error_code="INVALID_PDF")

        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.pdf")
        file.save(temp_path)

        try:
            complex_text = extract_text_with_ocr_fallback(temp_path)
            logger.info(
                "PDF uploaded: filename='%s' temp_path='%s'",
                safe_filename,
                temp_path,
            )
        except OSError as e:
            logger.exception("PDF processing failed due to system/file error for '%s': %s", temp_path, e)
            return api_error(
                "The uploaded PDF could not be processed.",
                400,
                error_code="PDF_PROCESSING_FAILED"
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if not complex_text.strip():
            return api_error(
                "The uploaded PDF contains no readable text.",
                400,
                error_code="EMPTY_PDF_TEXT"
            )

        scheme_name = os.path.splitext(safe_filename)[0]
        request_id = database.log_request(scheme_name, "pdf")

        try:
            ai_result = simplify_document(complex_text, scheme_name)
            logger.info(
                "Gemini called: scheme='%s' source='pdf'",
                scheme_name,
            )
        except (ValueError, RuntimeError) as e:
            logger.exception("Gemini simplification failed for scheme '%s': %s", scheme_name, e)
            return api_error(
                "AI could not simplify the document at this time.",
                502,
                error_code="AI_SIMPLIFICATION_FAILED"
            )

        audio_rel_path = generate_telugu_audio(ai_result["telugu"], scheme_name)
        voice_url = url_for("static", filename=audio_rel_path) if audio_rel_path else None

        return api_response({
            "request_id": request_id,
            "scheme_name": scheme_name,
            "level": "Uploaded PDF",
            "category": "Document",
            "source_name": "Uploaded PDF",
            "source_url": "",
            "simplified": ai_result["simplified"],
            "telugu": ai_result["telugu"],
            "voice_url": voice_url,
        })

    data = request.get_json(silent=True) or {}
    scheme_name = data.get("scheme_name")
    if not scheme_name:
        return api_error("Missing scheme_name", 400, error_code="MISSING_SCHEME_NAME")

    scheme_data = schemes.get(scheme_name)
    if not scheme_data:
        return api_error("Scheme not found", 404, error_code="SCHEME_NOT_FOUND")

    request_id = database.log_request(scheme_name, "catalog")
    return api_response(static_scheme_response(scheme_name, scheme_data, request_id))


@app.route("/analytics")
def analytics() -> Any:
    """Return analytics rendered from feedback stats."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT r.scheme_name,
               COUNT(f.id) AS feedback_count,
               ROUND(AVG(f.rating), 2) AS avg_rating
        FROM requests r
        LEFT JOIN feedback f ON r.id = f.request_id
        GROUP BY r.scheme_name
        ORDER BY feedback_count DESC, avg_rating DESC
    """)
    stats = cur.fetchall()
    conn.close()
    return render_template("analytics.html", stats=stats)


@app.route("/feedback", methods=["POST"])
@limiter.limit(feedback_limit)
def feedback() -> Any:
    """Receive feedback for a request and persist it."""
    data = request.get_json(silent=True) or {}
    if "request_id" not in data or "rating" not in data:
        return api_error("Missing request_id or rating", 400, error_code="MISSING_REQUEST_ID_OR_RATING")
    try:
        rating = int(data["rating"])
    except (TypeError, ValueError):
        return api_error("Rating must be a number", 400, error_code="INVALID_RATING")
    if rating < 1 or rating > 5:
        return api_error("Rating must be between 1 and 5", 400, error_code="INVALID_RATING_RANGE")
    try:
        database.save_feedback(data["request_id"], rating, data.get("comment", ""))
        logger.info(
            "Feedback submitted: request_id=%s rating=%s",
            data["request_id"],
            rating,
        )
        return api_response({"status": "success"})
    except sqlite3.Error as e:
        logger.exception("Feedback save failed in database for request_id=%s: %s", data["request_id"], e)
        return api_error("Unable to save feedback.", 500, error_code="FEEDBACK_SAVE_FAILED")


@app.route("/eligibility-check", methods=["POST"])
def eligibility_check() -> Any:
    """Evaluate basic eligibility answers for a scheme."""
    data = request.get_json(silent=True) or {}
    scheme_name = data.get("scheme_name")
    answers = data.get("answers", {})
    if not scheme_name or scheme_name not in schemes:
        return api_error("Scheme not found", 404, error_code="SCHEME_NOT_FOUND")
    
    # Ensure answers is a dictionary structure
    if not isinstance(answers, dict):
        return api_error("Answers must be a structured key-value object.", 400, error_code="INVALID_ANSWERS_TYPE")

    scheme = schemes[scheme_name]
    questions = scheme.get("eligibility_questions", [])
    if not questions:
        return api_response({
            "scheme_name": scheme_name,
            "likely_eligible": True,
            "message_te": "ఈ పథకం సర్వసాధారణ సేవ - ఎవరూ ఉపయోగించవచ్చు.",
            "message_en": "This is a general scheme - anyone can use it."
        })
    score = 0
    total_weight = 0
    for idx, question in enumerate(questions):
        weight = {"critical": 3, "high": 2, "medium": 1}.get(question.get("weight", "medium"), 1)
        total_weight += weight
        if answers.get(str(idx)) == "yes":
            score += weight
    eligibility_percentage = int((score / total_weight * 100)) if total_weight > 0 else 0
    return api_response({
        "scheme_name": scheme_name,
        "eligibility_percentage": eligibility_percentage,
        "likely_eligible": eligibility_percentage >= 60,
        "message_te": "అర్హత సంభవనీయమైనది" if eligibility_percentage >= 60 else "మరిన్ని వివరాలు చెక్ చేయండి",
        "message_en": "Likely eligible" if eligibility_percentage >= 60 else "Check details further",
        "next_step_te": f"అధికారిక {scheme.get('eligibility_confirmation', 'ఆఫీస్')} కు సందర్శించండి",
        "next_step_en": f"Visit official {scheme.get('eligibility_confirmation', 'office')}"
    })


@app.route("/document-checklist", methods=["GET"])
def document_checklist() -> Any:
    """Return a document checklist for a given scheme."""
    scheme_name = request.args.get("scheme_name")
    if not scheme_name or scheme_name not in schemes:
        return api_error("Scheme not found", 404, error_code="SCHEME_NOT_FOUND")
    scheme = schemes[scheme_name]
    required_docs = scheme.get("required_documents", [])
    return api_response({
        "scheme_name": scheme_name,
        "documents": required_docs,
        "instructions_te": "నిల్వ చేయడానికి ముందు కాపీలు తీసుకోండి.",
        "instructions_en": "Make copies before submission.",
        "warning_te": "ఆధార్, ప్రెస్క్రిప్షన్లు లేదా వ్యక్తిగత ఫైలులను అప్‌లోడ్ చేయవద్దు.",
        "warning_en": "Do not upload Aadhaar, prescriptions, or private files to this device."
    })


@app.route("/whatsapp-share", methods=["POST"])
def whatsapp_share() -> Any:
    """Build a WhatsApp share message for a scheme."""
    data = request.get_json(silent=True) or {}
    scheme_name = data.get("scheme_name")
    if not scheme_name or scheme_name not in schemes:
        return api_error("Scheme not found", 404, error_code="SCHEME_NOT_FOUND")
    scheme = schemes[scheme_name]
    message = f"""🏥 {scheme.get('telugu_name', scheme_name)}

📋 పథకం: {scheme_name}

✅ అర్హత:
{scheme.get('simplified', {}).get('eligibility', 'వివరాలు చూడండి')}

📄 పత్రాలు:
{', '.join([doc.get('name_te', doc.get('name', '')) for doc in scheme.get('required_documents', [])])}

📞 సంప్రదించండి: {scheme.get('eligibility_confirmation', 'Government office')}

🔗 మరిన్ని: {scheme.get('official_website', '')}"""
    database.log_whatsapp_share(scheme_name)
    return api_response({
        "scheme_name": scheme_name,
        "whatsapp_text": message,
        "whatsapp_api": f"https://wa.me/?text={urllib.parse.quote(message)}"
    })


@app.route("/enhanced-feedback", methods=["POST"])
@limiter.limit(feedback_limit)
def enhanced_feedback() -> Any:
    """Save extended feedback metadata for a request."""
    data = request.get_json(silent=True) or {}
    required_fields = ["request_id", "rating"]
    if not all(field in data for field in required_fields):
        return api_error(
            f"Missing required fields: {required_fields}",
            400,
            error_code="MISSING_REQUIRED_FIELDS"
        )
    try:
        rating = int(data["rating"])
        if rating < 1 or rating > 5:
            return api_error("Rating must be 1-5", 400, error_code="INVALID_RATING_RANGE")
    except (TypeError, ValueError):
        return api_error("Invalid rating", 400, error_code="INVALID_RATING")

    try:
        database.save_feedback(
            data["request_id"],
            rating,
            f"Clear: {data.get('was_clear', 'N/A')} | "
            f"Got benefit: {data.get('got_benefit', 'N/A')} | "
            f"Village: {data.get('village', 'N/A')} | "
            f"Problem: {data.get('problem', 'N/A')}"
        )
        logger.info(
            "Enhanced feedback submitted: request_id=%s rating=%s",
            data["request_id"],
            rating,
        )
        return api_response({"status": "success", "message": "Feedback saved successfully"})
    except sqlite3.Error as e:
        logger.exception("Enhanced feedback save failed in database for request_id=%s: %s", data["request_id"], e)
        return api_error("Unable to save feedback.", 500, error_code="FEEDBACK_SAVE_FAILED")


@app.route("/staff-report", methods=["POST"])
@limiter.limit(report_limit)
def staff_report() -> Any:
    """Accept staff reports and store them in the database."""
    data = request.get_json(silent=True) or {}
    required = ["scheme_name", "feedback_type"]
    if not all(f in data for f in required):
        return api_error("Missing required fields", 400, error_code="MISSING_REQUIRED_FIELDS")
    scheme_name = data.get("scheme_name")
    if scheme_name not in schemes:
        return api_error("Scheme not found", 404, error_code="SCHEME_NOT_FOUND")
    feedback_type = data.get("feedback_type")

    try:
        database.save_staff_feedback(
            scheme_name,
            data.get("village", ""),
            data.get("feedback_text", ""),
            feedback_type
        )
        logger.info(
            "Staff report submitted: scheme='%s' feedback_type='%s' village='%s'",
            scheme_name,
            feedback_type,
            data.get("village", ""),
        )
        return api_response({
            "status": "success",
            "message": "Thank you for helping improve this service",
            "message_te": "సేవ పెరుగుదలకు సహాయం చేసినందుకు ధన్యవాదాలు"
        })
    except sqlite3.Error as e:
        logger.exception("Staff feedback save failed in database for scheme='%s': %s", scheme_name, e)
        return api_error("Unable to save staff feedback.", 500, error_code="STAFF_FEEDBACK_SAVE_FAILED")


@app.route("/local-locations", methods=["GET"])
def local_locations() -> Any:
    """Return local help locations for a scheme and village."""
    scheme_name = request.args.get("scheme_name")
    village = request.args.get("village", "")
    if not scheme_name or scheme_name not in schemes:
        return api_error("Scheme not found", 404, error_code="SCHEME_NOT_FOUND")
    scheme = schemes[scheme_name]
    locations = scheme.get("local_help_locations", {})
    return api_response({
        "scheme_name": scheme_name,
        "village": village,
        "locations": locations,
        "note_te": "కృపయా భూ-తొందరకు సమీపకు ఆసుపత్రిని సందర్శించండి.",
        "note_en": "Please visit nearby hospital / health centre.",
        "emergency": "108" if "ambulance" in scheme.get("category", "").lower() else ""
    })


@app.route("/offline-cache", methods=["GET"])
def offline_cache() -> Any:
    """Return cached scheme metadata for offline clients."""
    return api_response({
        "schemes": len(schemes),
        "schemes_list": {
            name: {
                "telugu_name": data.get("telugu_name"),
                "category": data.get("category"),
                "simplified": data.get("simplified"),
                "telugu": data.get("telugu"),
                "last_updated": data.get("last_updated")
            }
            for name, data in schemes.items()
        },
        "emergency_numbers": {
            "ambulance": "108",
            "health_advice": "104",
            "phc_help": "Check your village"
        },
        "timestamp": datetime.utcnow().isoformat()
    })


if __name__ == "__main__":
    logger.info("Starting SmartGovAI server...")
    app.run(debug=DEBUG_MODE, host=SERVER_HOST, port=SERVER_PORT)