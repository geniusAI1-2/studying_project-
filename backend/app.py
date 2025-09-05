from flask import Flask, request, jsonify
import requests
import os
import uuid
import subprocess
import validators
import requests
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)

AI_BASE_URL = "http://127.0.0.1:8000"  # Where your AI APIs are running

ALLOWED_PDF = {"pdf"}
ALLOWED_AUDIO = {"mp3", "wav", "m4a"}

# ==========================
# HELPERS
# ==========================
def allowed_file(filename, allowed_exts):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts

def forward_post(endpoint: str, payload=None, files=None):
    """Forward request to AI service and wrap response"""
    try:
        url = f"{AI_BASE_URL}{endpoint}"
        r = requests.post(url, json=payload, files=files, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}, 500

def wrap_response(inputs, ai_response):
    """Standardized response structure"""
    return {
        "inputs_received": inputs,
        "ai_response": ai_response
    }

#-----------------------------------------------------------------------
# File 1 : 
#-----------------------------------------------------------------------
# ----------------- Helper for validation -----------------
def require_fields(data, fields):
    """
    Ensure required fields exist in the request.
    Returns (True, None) if valid, (False, error_message) if missing fields.
    """
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return False, f"Missing required field(s): {', '.join(missing)}"
    return True, None

# ----------------- 1) GET SCRIPT -----------------
@app.route("/getting_script_from_video", methods=["POST"])
def getting_script_from_video():
    try:
        data = request.json or {}

        # Support batch requests
        if isinstance(data.get("requests"), list):
            results = []
            for item in data["requests"]:
                valid, error = require_fields(item, ["input_link", "language"])
                if not valid:
                    results.append({"id": item.get("id"), "error": error})
                    continue

                payload = {"input_link": item["input_link"], "language": item["language"]}
                response = requests.post("http://127.0.0.1:8000/getting_script", json=payload)

                if response.status_code != 200:
                    results.append({"id": item.get("id"), "error": response.text})
                else:
                    results.append({"id": item.get("id"), "response": response.json()})

            return jsonify({"results": results})

        # Single request
        valid, error = require_fields(data, ["input_link", "language"])
        if not valid:
            return jsonify({"error": error}), 400

        payload = {"input_link": data["input_link"], "language": data["language"]}
        response = requests.post("http://127.0.0.1:8000/getting_script", json=payload)

        if response.status_code != 200:
            return jsonify({"error": "Script API failed", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------- 2) SUMMARIZE -----------------
@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.json or {}

        if isinstance(data.get("requests"), list):
            results = []
            for item in data["requests"]:
                valid, error = require_fields(item, ["input_text"])
                if not valid:
                    results.append({"id": item.get("id"), "error": error})
                    continue

                payload = {"input_text": item["input_text"]}
                response = requests.post("http://127.0.0.1:8000/summarize", json=payload)

                if response.status_code != 200:
                    results.append({"id": item.get("id"), "error": response.text})
                else:
                    results.append({"id": item.get("id"), "response": response.json()})

            return jsonify({"results": results})

        valid, error = require_fields(data, ["input_text"])
        if not valid:
            return jsonify({"error": error}), 400

        payload = {"input_text": data["input_text"]}
        response = requests.post("http://127.0.0.1:8000/summarize", json=payload)

        if response.status_code != 200:
            return jsonify({"error": "Summarize API failed", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------- 3) CHAT -----------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}

        if isinstance(data.get("requests"), list):
            results = []
            for item in data["requests"]:
                valid, error = require_fields(item, ["input_text", "question"])
                if not valid:
                    results.append({"id": item.get("id"), "error": error})
                    continue

                payload = {"input_text": item["input_text"], "question": item["question"]}
                response = requests.post("http://127.0.0.1:8000/chat", json=payload)

                if response.status_code != 200:
                    results.append({"id": item.get("id"), "error": response.text})
                else:
                    results.append({"id": item.get("id"), "response": response.json()})

            return jsonify({"results": results})

        valid, error = require_fields(data, ["input_text", "question"])
        if not valid:
            return jsonify({"error": error}), 400

        payload = {"input_text": data["input_text"], "question": data["question"]}
        response = requests.post("http://127.0.0.1:8000/chat", json=payload)

        if response.status_code != 200:
            return jsonify({"error": "Chat API failed", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------- 4) EXTRACT MAIN POINTS -----------------
@app.route("/extract_main_points", methods=["POST"])
def extract_main_points():
    try:
        data = request.json or {}

        if isinstance(data.get("requests"), list):
            results = []
            for item in data["requests"]:
                valid, error = require_fields(item, ["input_text"])
                if not valid:
                    results.append({"id": item.get("id"), "error": error})
                    continue

                payload = {"input_text": item["input_text"]}
                response = requests.post("http://127.0.0.1:8000/extract_main_points", json=payload)

                if response.status_code != 200:
                    results.append({"id": item.get("id"), "error": response.text})
                else:
                    results.append({"id": item.get("id"), "response": response.json()})

            return jsonify({"results": results})

        valid, error = require_fields(data, ["input_text"])
        if not valid:
            return jsonify({"error": error}), 400

        payload = {"input_text": data["input_text"]}
        response = requests.post("http://127.0.0.1:8000/extract_main_points", json=payload)

        if response.status_code != 200:
            return jsonify({"error": "Extract API failed", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#-----------------------------------------------------------------------
# File 2 : 
#-----------------------------------------------------------------------

def require_fields(data, fields):
    for field in fields:
        if field not in data or data[field] in [None, ""]:
            return False, f"Missing or empty required field: {field}"
    return True, None


# ---------------------
# Upload PDF API
# ---------------------

@app.route("/backend/file2/upload_pdf", methods=["POST"])
def backend_upload_pdf_file2():
    try:
        if "file" not in request.files:
            return jsonify({"error": "PDF file is required"}), 400

        file = request.files["file"]
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Read the file content as bytes
        file_bytes = file.read()

        # Prepare files for requests: (filename, bytes, mimetype)
        files = {"file": (file.filename, file_bytes, file.mimetype)}
        params = {"index_path": request.form.get("index_path", "faiss_index")}
        print(f"params : {params}")

        response = requests.post(
            f"{AI_BASE_URL}/upload_pdf",
            files=files,
            params=params
        )

        if response.status_code != 200:
            return jsonify({
                "error": "AI upload API failed",
                "details": response.text
            }), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------
# Ask Question API
# ---------------------
@app.route("/backend/file2/ask", methods=["POST"])
def backend_ask_file2():
    try:
        data = request.json or {}

        # Validate required fields
        valid, error = require_fields(data, ["question"])
        if not valid:
            return jsonify({"error": error}), 400

        payload = {
            "question": data["question"],
            "prev_question": data.get("prev_question")
        }
        params = {"index_path": data.get("index_path", "faiss_index")}
        response = requests.post(f"{AI_BASE_URL}/ask", json=payload, params=params)

        if response.status_code != 200:
            return jsonify({"error": "AI ask API failed", "details": response.text}), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#-----------------------------------------------------------------------
# File 3 : 
#-----------------------------------------------------------------------

# ==========================
# APIs
# ==========================

@app.route("/backend/file3/get_script", methods=["POST"])
def backend_get_scrip_file3t():
    data = request.json or {}
    youtube_url = data.get("input_link")
    language = data.get("language", "en")
    index_name = data.get("index_name")

    # Validations
    if not youtube_url or not validators.url(youtube_url):
        return jsonify({"error": "Invalid YouTube URL"}), 400
    if not index_name:
        return jsonify({"error": "Index name required"}), 400

    ai_resp = forward_post("/getting_script", payload=data)
    return jsonify(wrap_response(data, ai_resp))

# ---------------------
# Upload PDF API (file3 version) -> connects to AI API
# ---------------------
@app.route("/backend/file3/upload_pdf", methods=["POST"])
def backend_upload_pdf_file3():
    try:
        # ✅ Validate file existence
        if "file" not in request.files:
            return jsonify({"error": "PDF file is required"}), 400

        file = request.files["file"]
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # ✅ Read file bytes
        file_bytes = file.read()

        # ✅ Ensure index_name exists (default if missing)
        index_name = request.form.get("index_name")
        if not index_name:
            index_name = "faiss_index"

        # ✅ Prepare request for AI API (form-data)
        files = {"file": (file.filename, file_bytes, file.mimetype)}
        data = {"index_name": index_name}

        # print(f"[file3] Forwarding → file={file.filename}, index_name={index_name}")

        # ✅ Forward to AI API
        response = requests.post(
            f"{AI_BASE_URL}/upload_pdf",
            files=files,
            data=data,
            timeout=60  # avoid hanging
        )

        # ✅ Return AI API response transparently
        if response.status_code != 200:
            return jsonify({
                "error": "AI upload API failed",
                "details": response.text
            }), response.status_code

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/backend/file3/generate_questions", methods=["POST"])
def backend_generate_questions_file3():
    data = request.json or {}
    if not data.get("index_name") or not data.get("subject") or not data.get("num_questions") or not data.get("question_type") :
        return jsonify({"error": "index_name, subject, and num_questions are required"}), 400

    ai_resp = forward_post("/generate_questions", payload=data)
    return jsonify(wrap_response(data, ai_resp))


@app.route("/backend/file3/evaluation", methods=["POST"])
def backend_evaluation_file3():
    data = request.json or {}
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    if not (len(data.get("questions", [])) == len(data.get("student_answers", [])) == len(data.get("correct_answers", []))):
        return jsonify({"error": "Questions, student_answers, and correct_answers must have same length"}), 400

    ai_resp = forward_post("/evaluation", payload=data)
    return jsonify(wrap_response(data, ai_resp))

@app.route("/backend/voice_script", methods=["POST"])
def backend_voice_script_file3():
    if "file" not in request.files or "index_name" not in request.form:
        return jsonify({"error": "Audio file and index_name are required"}), 400

    file = request.files["file"]
    index_name = request.form["index_name"]

    if file.filename == "" or not allowed_file(file.filename, ALLOWED_AUDIO):
        return jsonify({"error": "Invalid or missing audio file"}), 400

    filename = secure_filename(file.filename)

    # ✅ Read file into memory
    file_bytes = file.read()

    # ✅ Build proper multipart/form-data for FastAPI
    files = {"file": (filename, file_bytes, "audio/mpeg")}
    data = {"index_name": index_name}

    try:
        # ✅ Call AI API correctly (files + form-data, not JSON)
        response = requests.post(
            f"{AI_BASE_URL}/voice_script",
            files=files,
            data=data,
            timeout=120
        )
        response.raise_for_status()

        ai_resp = response.json()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(wrap_response(
        {"index_name": index_name, "file_name": filename},
        ai_resp
    ))

@app.route("/backend/file3/math_physics", methods=["POST"])
def backend_math_physics_file3():
    data = request.json or {}
    if not data.get("input_Q"):
        return jsonify({"error": "input_Q is required"}), 400

    ai_resp = forward_post("/math&physics", payload=data)
    return jsonify(wrap_response(data, ai_resp))


# ==========================
# RUN AI-GENERATED PLOT CODE
# ==========================
@app.route("/backend/run_plot", methods=["POST"])
def run_plot_file3():
    data = request.json or {}
    code = data.get("drawing_code")
    if not code:
        return jsonify({"error": "No drawing_code provided"}), 400

    file_id = uuid.uuid4().hex
    py_file = f"plot_{file_id}.py"
    img_file = f"plot_{file_id}.png"

    # Ensure plot is saved with unique name
    code = code.replace("plot.png", img_file)

    with open(py_file, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        subprocess.run(["python", py_file], check=True, timeout=10)
        if os.path.exists(img_file):
            return send_file(img_file, mimetype="image/png")
        else:
            return jsonify({"error": "Image not generated"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Plot execution timeout"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(py_file): os.remove(py_file)
        # You may also schedule cleanup for img files later

# ==========================
# HEALTHCHECK
# ==========================
@app.route("/backend/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify({
        "status": "ok",
        "ai_base_url": AI_BASE_URL
    })


#-----------------------------------------------------------------------
# File 4 : 
#-----------------------------------------------------------------------

# Base URL of your FastAPI AI service
AI_API_BASE = AI_BASE_URL   # change to your FastAPI service URL

# ---------------------------
# Helper Functions
# ---------------------------

from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime


SESSIONS_FILE = "sessions.json"

# -----------------------------
# JSON Storage Helpers
# -----------------------------
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_sessions(data):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_session(session_id):
    sessions = load_sessions()
    return sessions.get(session_id)


def save_session(session_data):
    sessions = load_sessions()
    sessions[session_data["session_id"]] = session_data
    save_sessions(sessions)


# -----------------------------
# API Helpers
# -----------------------------
def forward_get(endpoint: str, params: dict = None):
    try:
        resp = requests.get(f"{AI_API_BASE}{endpoint}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def forward_post(endpoint: str, payload: dict):
    try:
        resp = requests.post(f"{AI_API_BASE}{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def wrap_response(input_data, ai_response):
    return {"input": input_data, "ai_output": ai_response}

# ---------------------------
# Backend Routes
# ---------------------------
@app.route("/backend/health", methods=["GET"])
def backend_health():
    ai_resp = forward_get("/health")
    return jsonify(wrap_response({}, ai_resp))

@app.route("/backend/select-language", methods=["POST"])
def backend_select_language():
    data = request.json or {}
    if not data.get("language"):
        return jsonify({"error": "language is required"}), 400

    ai_resp = forward_post("/select-language", {"language": data["language"]})

    # Persist session if FastAPI returned one
    if isinstance(ai_resp, dict) and ai_resp.get("session_id"):
        session_data = {
            "session_id": ai_resp["session_id"],
            "language": ai_resp["language"],
            "current_lesson": ai_resp["current_lesson"],
            "completed_lessons": [],
            "chat_history": [],
            "created_at": datetime.now().isoformat()
        }
        save_session(session_data)

    return jsonify(wrap_response(data, ai_resp))

@app.route("/backend/get-lesson/<int:lesson_number>", methods=["GET"])
def backend_get_lesson(lesson_number):
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    ai_resp = forward_get(f"/lesson/{lesson_number}")

    return jsonify(wrap_response({"lesson_number": lesson_number}, ai_resp))


@app.route("/backend/ask-tutor", methods=["POST"])
def backend_ask_tutor():
    data = request.json or {}
    session_id = data.get("session_id")
    if not session_id or not data.get("question"):
        return jsonify({"error": "session_id and question are required"}), 400

    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    ai_resp = forward_post("/ask-tutor", {"question": data["question"]})

    # update chat history
    if isinstance(ai_resp, dict) and "response" in ai_resp:
        session["chat_history"].append({
            "user": data["question"],
            "assistant": ai_resp["response"],
            "timestamp": datetime.now().isoformat()
        })
        save_session(session)

    return jsonify(wrap_response(data, ai_resp))

@app.route("/backend/generate-quiz/<int:lesson_number>", methods=["GET"])
def backend_generate_quiz(lesson_number):
    ai_resp = forward_get(f"/generate-quiz/{lesson_number}")
    return jsonify(wrap_response({"lesson_number": lesson_number}, ai_resp))

@app.route("/backend/submit-quiz", methods=["POST"])
def backend_submit_quiz():
    data = request.json or {}

    # Validation
    if not data.get("lesson_id"):
        return jsonify({"error": "lesson_id is required"}), 400
    if not isinstance(data.get("answers"), list):
        return jsonify({"error": "answers must be a list"}), 400

    ai_resp = forward_post("/submit-quiz", payload=data)
    return jsonify(wrap_response(data, ai_resp))


@app.route("/backend/session-status", methods=["GET"])
def backend_session_status():
    ai_resp = forward_get("/session-status")
    return jsonify(wrap_response({}, ai_resp))


@app.route("/backend/available-languages", methods=["GET"])
def backend_available_languages():
    ai_resp = forward_get("/available-languages")
    return jsonify(wrap_response({}, ai_resp))


import requests

def forward_gets(endpoint):
    url = f"http://127.0.0.1:8000{endpoint}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        # If AI returns JSON error, parse it
        try:
            return resp.json()
        except Exception:
            return {"error": str(e), "response_text": resp.text}
    except Exception as e:
        return {"error": str(e)}

def forward_posts(endpoint, payload):
    url = f"http://127.0.0.1:8000{endpoint}"
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        try:
            return resp.json()
        except Exception:
            return {"error": str(e), "response_text": resp.text}
    except Exception as e:
        return {"error": str(e)}


@app.route("/backend/generate-coding-challenge", methods=["GET"])
def backend_generate_coding_challenge():
    ai_resp = forward_gets("/generate-coding-challenge")
    return jsonify(wrap_response({}, ai_resp))


@app.route("/backend/submit-code", methods=["POST"])
def backend_submit_code():
    data = request.json or {}

    if not data.get("challenge_id"):
        return jsonify({"error": "challenge_id is required"}), 400
    if not data.get("code"):
        return jsonify({"error": "code is required"}), 400

    ai_resp = forward_posts("/submit-code", payload=data)
    return jsonify(wrap_response(data, ai_resp))


# -----------------------------
# Backend Routes
# -----------------------------


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
