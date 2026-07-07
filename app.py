import json
import os
import uuid
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from config import (
    BASE_DIR,
    SCHEMES_PATH,
    UPLOAD_DIR,
    AUDIO_DIR,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_UPLOAD_SIZE,
    MODEL_NAME,
)

from logger_config import logger
from utils import allowed_file, voice_text

from flask import Flask, jsonify, render_template, request, url_for
from gtts import gTTS
import pdfplumber

import database

try:
    from google import genai
    from google.genai import types
except ImportError:
    logging.exception("Failed to import Google GenAI SDK.")
    genai = None
    types = None

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False






app = Flask(__name__)

# Feature status logging (no secrets)
logger.info("Gemini AI: %s", "Enabled" if genai and os.environ.get("GEMINI_API_KEY") else "Disabled")
logger.info("OCR support: %s", "Available" if OCR_AVAILABLE else "Not installed")

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
secret_key = os.environ.get("SECRET_KEY", "").strip()
if not secret_key:
    raise RuntimeError("SECRET_KEY is not set. Please add it to your .env file.")
app.secret_key = secret_key

database.init_db()
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

api_key = os.environ.get("GEMINI_API_KEY", "").strip()
if genai and api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

if not api_key:
    logger.warning("GEMINI_API_KEY not found. PDF simplification will be disabled.")

  


def load_schemes() -> Dict[str, Any]:
    """Load the schemes database from JSON file."""
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Load schemes safely
try:
    schemes = load_schemes()
except Exception:
    logger.exception("Failed to load schemes database.")
    raise





def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_with_ocr_fallback(file_path: str) -> str:
    """Extract text with OCR fallback if normal extraction yields little content."""
    text = extract_text_from_pdf(file_path)
    if len(text) > 100:
        return text
    if not OCR_AVAILABLE:
        return text
    try:
        images = convert_from_path(file_path, dpi=200)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img, lang="tel+eng") + "\n"
        return ocr_text.strip()
    except Exception:
        logger.exception("OCR processing failed.")
        return text


def call_gemini_simplify(complex_text: str, scheme_name: str) -> Dict[str, Any]:
    """Call Gemini API to simplify a scheme document."""
    if client is None:
        raise RuntimeError(
            "PDF simplification needs GEMINI_API_KEY. Built-in health schemes still work."
        )
    prompt = f"""
You simplify Indian government health scheme documents for rural Andhra Pradesh citizens.

Scheme/document name: {scheme_name}
Text:
\"\"\"{complex_text}\"\"\"

Return simple, accurate information. Do not invent benefits that are not present in the text.
Use easy English, then translate to clear Telugu.

Return strictly this JSON object:
{{
  "simplified": {{
    "eligibility": "Who can apply?",
    "benefits": "What do they get?",
    "documents": "What documents are needed?",
    "steps": "How to apply step by step?"
  }},
  "telugu": {{
    "eligibility": "Telugu translation of eligibility",
    "benefits": "Telugu translation of benefits",
    "documents": "Telugu translation of documents",
    "steps": "Telugu translation of steps"
  }}
}}
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        logger.exception("Gemini returned invalid JSON.")
        raise ValueError("Invalid AI response.")
    if "simplified" not in result or "telugu" not in result:
        raise ValueError("Gemini returned an unexpected shape")
    return result



def audio_url_from_static_path(static_path: Optional[str]) -> Optional[str]:
    """Return a Flask URL for an existing audio file, or None if invalid."""
    if not static_path:
        return None
    static_path = static_path.replace("\\", "/")
    abs_path = os.path.join(BASE_DIR, static_path)
    if os.path.exists(abs_path) and os.path.getsize(abs_path) > 0:
        return url_for("static", filename=static_path.removeprefix("static/"))
    return None


def generate_telugu_audio(
    telugu_data: Dict[str, str],
    scheme_name: str,
    static_path: Optional[str] = None,
) -> Optional[str]:
    """Generate Telugu audio for the scheme if not already present."""
    existing_url = audio_url_from_static_path(static_path)
    if existing_url:
        return existing_url
    if static_path:
        filename = os.path.join(BASE_DIR, static_path)
    else:
        filename = os.path.join(AUDIO_DIR, f"{uuid.uuid4()}.mp3")
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        tts = gTTS(text=voice_text(telugu_data, scheme_name), lang="te", slow=False)
        tts.save(filename)
        rel_path = os.path.relpath(filename, os.path.join(BASE_DIR, "static")).replace("\\", "/")
        return url_for("static", filename=rel_path)
    except Exception:
        logger.exception("Audio generation failed for scheme '%s'.", scheme_name)
        return None


def static_scheme_response(scheme_name: str, scheme_data: Dict[str, Any], request_id: int) -> Dict[str, Any]:
    """Build the standard response for a built‑in scheme."""
    return {
        "request_id": request_id,
        "scheme_name": scheme_name,
        "level": scheme_data.get("level", ""),
        "category": scheme_data.get("category", ""),
        "source_name": scheme_data.get("source_name", "Official source"),
        "source_url": scheme_data.get("source_url", ""),
        "simplified": scheme_data["simplified"],
        "telugu": scheme_data["telugu"],
        "voice_url": generate_telugu_audio(
            scheme_data["telugu"],
            scheme_name,
            scheme_data.get("audio_file"),
        ),
    }


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "File too large. Please upload a PDF below 10 MB."}), 413

@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Resource not found."}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.exception("Unhandled server error: %s", error)
    return jsonify({"error": "An unexpected server error occurred."}), 500

@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    logger.exception("Unhandled exception: %s", error)
    return jsonify({"error": "An unexpected error occurred."}), 500


@app.route("/")
def index():
    return render_template("index.html", schemes=schemes, scheme_names=list(schemes.keys()))

@app.route("/offline.html")
def offline():
    return render_template("offline.html")

@app.route("/healthz")
def healthz():
    """Health check endpoint – verifies schemes and directories."""
    health_status = {
        "status": "ok",
        "schemes": len(schemes),
        "gemini_pdf_support": client is not None,
        "checks": {
            "upload_dir": "ok" if os.path.exists(UPLOAD_DIR) and os.access(UPLOAD_DIR, os.W_OK) else "failed",
            "audio_dir": "ok" if os.path.exists(AUDIO_DIR) and os.access(AUDIO_DIR, os.W_OK) else "failed",
        }
    }
    # If either directory check failed, degrade status (but don't expose internals)
    if health_status["checks"]["upload_dir"] != "ok" or health_status["checks"]["audio_dir"] != "ok":
        health_status["status"] = "degraded"
        logger.warning("Health check: directory accessibility issue.")
    return jsonify(health_status)


@app.route("/simplify", methods=["POST"])
def simplify():
    file = request.files.get("document")
    if file:
        valid, result = allowed_file(file)
        if not valid:
            return jsonify({"error": result}), 400

        safe_filename = result
        if client is None:
            logger.error("PDF simplification attempted but GEMINI_API_KEY is not set.")
            return jsonify({"error": "PDF simplification is currently unavailable. Please try again later."}), 503

        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.pdf")
        file.save(temp_path)
        try:
            complex_text = extract_text_with_ocr_fallback(temp_path)
        except Exception:
            logger.exception("Failed to process uploaded PDF.")
            return jsonify({"error": "The uploaded PDF could not be processed."}), 400
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if not complex_text.strip():
            return jsonify({"error": "The uploaded PDF contains no readable text."}), 400

        scheme_name = os.path.splitext(safe_filename)[0]
        request_id = database.log_request(scheme_name, "pdf")

        try:
            ai_result = call_gemini_simplify(complex_text, scheme_name)
        except Exception:
            logger.exception("Gemini simplification failed.")
            return jsonify({"error": "AI could not simplify the document at this time."}), 502

        return jsonify({
            "request_id": request_id,
            "scheme_name": scheme_name,
            "level": "Uploaded PDF",
            "category": "Document",
            "source_name": "Uploaded PDF",
            "source_url": "",
            "simplified": ai_result["simplified"],
            "telugu": ai_result["telugu"],
            "voice_url": generate_telugu_audio(ai_result["telugu"], scheme_name),
        })

    data = request.get_json(silent=True) or {}
    scheme_name = data.get("scheme_name")
    if not scheme_name:
        return jsonify({"error": "Missing scheme_name"}), 400

    scheme_data = schemes.get(scheme_name)
    if not scheme_data:
        return jsonify({"error": "Scheme not found"}), 404

    request_id = database.log_request(scheme_name, "catalog")
    return jsonify(static_scheme_response(scheme_name, scheme_data, request_id))


@app.route("/analytics")
def analytics():
    import sqlite3
    conn = sqlite3.connect(os.path.join(BASE_DIR, "feedback.db"))
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
def feedback():
    data = request.get_json(silent=True) or {}
    if "request_id" not in data or "rating" not in data:
        return jsonify({"error": "Missing request_id or rating"}), 400
    try:
        rating = int(data["rating"])
    except (TypeError, ValueError):
        return jsonify({"error": "Rating must be a number"}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400
    try:
        database.save_feedback(data["request_id"], rating, data.get("comment", ""))
        return jsonify({"status": "success"})
    except Exception:
        logger.exception("Failed to save feedback.")
        return jsonify({"error": "Unable to save feedback."}), 500


# ==================== NEW FEATURES ====================

@app.route("/eligibility-check", methods=["POST"])
def eligibility_check():
    data = request.get_json(silent=True) or {}
    scheme_name = data.get("scheme_name")
    answers = data.get("answers", {})
    if not scheme_name or scheme_name not in schemes:
        return jsonify({"error": "Scheme not found"}), 404
    scheme = schemes[scheme_name]
    questions = scheme.get("eligibility_questions", [])
    if not questions:
        return jsonify({
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
    return jsonify({
        "scheme_name": scheme_name,
        "eligibility_percentage": eligibility_percentage,
        "likely_eligible": eligibility_percentage >= 60,
        "message_te": "అర్హత సంభవనీయమైనది" if eligibility_percentage >= 60 else "మరిన్ని వివరాలు చెక్ చేయండి",
        "message_en": "Likely eligible" if eligibility_percentage >= 60 else "Check details further",
        "next_step_te": f"అధికారిక {scheme.get('eligibility_confirmation', 'ఆఫీస్')} కు సందర్శించండి",
        "next_step_en": f"Visit official {scheme.get('eligibility_confirmation', 'office')}"
    })


@app.route("/document-checklist", methods=["GET"])
def document_checklist():
    scheme_name = request.args.get("scheme_name")
    if not scheme_name or scheme_name not in schemes:
        return jsonify({"error": "Scheme not found"}), 404
    scheme = schemes[scheme_name]
    required_docs = scheme.get("required_documents", [])
    return jsonify({
        "scheme_name": scheme_name,
        "documents": required_docs,
        "instructions_te": "నిల్వ చేయడానికి ముందు కాపీలు తీసుకోండి.",
        "instructions_en": "Make copies before submission.",
        "warning_te": "ఆధార్, ప్రెస్క్రిప్షన్లు లేదా వ్యక్తిగత ఫైలులను అప్‌లోడ్ చేయవద్దు.",
        "warning_en": "Do not upload Aadhaar, prescriptions, or private files to this device."
    })


@app.route("/whatsapp-share", methods=["POST"])
def whatsapp_share():
    data = request.get_json(silent=True) or {}
    scheme_name = data.get("scheme_name")
    if not scheme_name or scheme_name not in schemes:
        return jsonify({"error": "Scheme not found"}), 404
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
    return jsonify({
        "scheme_name": scheme_name,
        "whatsapp_text": message,
        "whatsapp_api": f"https://wa.me/?text={urllib.parse.quote(message)}"
    })


@app.route("/enhanced-feedback", methods=["POST"])
def enhanced_feedback():
    data = request.get_json(silent=True) or {}
    required_fields = ["request_id", "rating"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400
    try:
        rating = int(data["rating"])
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be 1-5"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid rating"}), 400

    try:
        database.save_feedback(
            data["request_id"],
            rating,
            f"Clear: {data.get('was_clear', 'N/A')} | "
            f"Got benefit: {data.get('got_benefit', 'N/A')} | "
            f"Village: {data.get('village', 'N/A')} | "
            f"Problem: {data.get('problem', 'N/A')}"
        )
        return jsonify({"status": "success", "message": "Feedback saved successfully"})
    except Exception:
        logger.exception("Enhanced feedback database save failed.")
        return jsonify({"error": "Unable to save feedback."}), 500


@app.route("/staff-report", methods=["POST"])
def staff_report():
    data = request.get_json(silent=True) or {}
    required = ["scheme_name", "feedback_type"]
    if not all(f in data for f in required):
        return jsonify({"error": "Missing required fields"}), 400
    scheme_name = data.get("scheme_name")
    if scheme_name not in schemes:
        return jsonify({"error": "Scheme not found"}), 404
    feedback_type = data.get("feedback_type")

    try:
        database.save_staff_feedback(
            scheme_name,
            data.get("village", ""),
            data.get("feedback_text", ""),
            feedback_type
        )
        return jsonify({
            "status": "success",
            "message": "Thank you for helping improve this service",
            "message_te": "సేవ పెరుగుదలకు సహాయం చేసినందుకు ధన్యవాదాలు"
        })
    except Exception:
        logger.exception("Staff feedback database save failed.")
        return jsonify({"error": "Unable to save staff feedback."}), 500


@app.route("/local-locations", methods=["GET"])
def local_locations():
    scheme_name = request.args.get("scheme_name")
    village = request.args.get("village", "")
    if not scheme_name or scheme_name not in schemes:
        return jsonify({"error": "Scheme not found"}), 404
    scheme = schemes[scheme_name]
    locations = scheme.get("local_help_locations", {})
    return jsonify({
        "scheme_name": scheme_name,
        "village": village,
        "locations": locations,
        "note_te": "కృపయా భూ-తొందరకు సమీపకు ఆసుపత్రిని సందర్శించండి.",
        "note_en": "Please visit nearby hospital / health centre.",
        "emergency": "108" if "ambulance" in scheme.get("category", "").lower() else ""
    })


@app.route("/offline-cache", methods=["GET"])
def offline_cache():
    return jsonify({
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
    app.run(debug=False, host="0.0.0.0", port=5000)