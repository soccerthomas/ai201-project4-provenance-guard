from flask import Flask, request, jsonify
import uuid
from datetime import datetime

from detector import detect_ai
from logger import write_log, get_log

app = Flask(__name__)


@app.route("/")
def home():
    return "AI Provenance Guard is running!"


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text or not creator_id:
        return jsonify({"error": "Missing text or creator_id"}), 400

    content_id = str(uuid.uuid4())

    # First detection signal (Groq)
    llm_score = detect_ai(text)

    # Placeholder values for Milestone 3
    confidence = llm_score
    attribution = "likely_ai" if llm_score >= 0.7 else "likely_human"
    label = "Placeholder label"

    # Audit log entry
    entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.utcnow().isoformat(),
        "llm_score": llm_score,
        "confidence": confidence,
        "attribution": attribution,
        "status": "classified"
    }

    write_log(entry)

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label
    })


@app.route("/log", methods=["GET"])
def log():
    return jsonify({
        "entries": get_log()
    })


if __name__ == "__main__":
    app.run(debug=True)