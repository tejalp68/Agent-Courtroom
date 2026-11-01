"""Agent Courtroom - a small Flask web UI.

Run with:  uv run app.py
Then open: http://127.0.0.1:5000
"""

import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# Existing project code (we only import from it, never change it)
from courtroom import trial
from agents.reporter import reporter

app = Flask(__name__)

# Paths are built from this file's location, so it works from any folder
BASE_DIR = Path(__file__).resolve().parent
TRACES_DIR = BASE_DIR / "traces"
REPORT_FILE = BASE_DIR / "report.json"


# ---------- helpers ----------

def error_response(error, default_message="Something went wrong."):
    """Turn an exception into a friendly {"error": ...} JSON response."""
    text = str(error)

    # Safety: never leak the API key in an error message
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        text = text.replace(key, "***")

    lowered = text.lower()
    if "429" in text or "quota" in lowered or "resource_exhausted" in lowered:
        return jsonify({"error": "Gemini quota exceeded (429). Wait a minute and try again."}), 429
    if "api key" in lowered or "api_key" in lowered or "401" in text or "403" in text:
        return jsonify({"error": "Missing or invalid GOOGLE_API_KEY. Check your .env file."}), 500
    if isinstance(error, (json.JSONDecodeError, KeyError, ValueError)):
        return jsonify({"error": "The judge returned a verdict that could not be read. Please try again."}), 502
    return jsonify({"error": f"{default_message} ({type(error).__name__})"}), 500


def safe_trace_name(name):
    """A trace name must be a plain file name: no slashes and no '..'."""
    return bool(name) and "/" not in name and "\\" not in name and ".." not in name


def load_trace(name):
    """Load traces/<name>.json, or return None if it does not exist."""
    path = TRACES_DIR / f"{name}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_history():
    """Read report.json. Missing or broken file means an empty list."""
    if not REPORT_FILE.is_file():
        return []
    try:
        data = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_history(history):
    REPORT_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


# ---------- routes ----------

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/traces")
def api_traces():
    """List the trace file names (without .json)."""
    if not TRACES_DIR.is_dir():
        return jsonify([])
    names = sorted(p.stem for p in TRACES_DIR.glob("*.json"))
    return jsonify(names)


@app.get("/api/trace/<name>")
def api_trace(name):
    """Return one trace (task + steps)."""
    if not safe_trace_name(name):
        return jsonify({"error": "Invalid trace name."}), 400
    try:
        trace = load_trace(name)
    except Exception as e:
        return error_response(e, "Could not read that trace.")
    if trace is None:
        return jsonify({"error": f"Trace '{name}' not found."}), 404
    return jsonify(trace)


@app.post("/api/trial")
def api_trial():
    """Put a trace on trial and save the verdict."""
    body = request.get_json(silent=True) or {}
    name = body.get("name", "")
    if not isinstance(name, str) or not safe_trace_name(name):
        return jsonify({"error": "Invalid trace name."}), 400

    try:
        trace = load_trace(name)
    except Exception as e:
        return error_response(e, "Could not read that trace.")
    if trace is None:
        return jsonify({"error": f"Trace '{name}' not found."}), 404

    try:
        outcome = trial(trace)  # several Gemini calls, takes a few seconds
    except Exception as e:
        return error_response(e, "The trial failed.")

    # Save the verdict to report.json
    try:
        history = load_history()
        history.append(outcome["result"])
        save_history(history)
    except Exception as e:
        return error_response(e, "The trial worked but saving the verdict failed.")

    return jsonify(outcome)


@app.get("/api/history")
def api_history():
    return jsonify(load_history())


@app.get("/api/summary")
def api_summary():
    """The reporter's summary of all saved verdicts."""
    history = load_history()
    if not history:
        return jsonify("")
    try:
        return jsonify(reporter(history))
    except Exception as e:
        return error_response(e, "Could not write the summary.")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
