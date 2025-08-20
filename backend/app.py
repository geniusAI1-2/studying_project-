from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
