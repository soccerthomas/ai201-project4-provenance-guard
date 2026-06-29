from flask import Flask, request, jsonify
import uuid
from datetime import datetime

from detector import detect_ai
from stylometric import compute_heuristic_score
from scoring import compute_confidence, get_attribution
from labels import generate_label
from logger import write_log, get_log, update_status
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day", "10 per minute"])
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

    llm_score = detect_ai(text)
    heuristic_score = compute_heuristic_score(text)
    confidence = compute_confidence(llm_score, heuristic_score)
    attribution = get_attribution(confidence)
    label = generate_label(attribution, confidence)

    entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "llm_score": llm_score,
        "heuristic_score": heuristic_score,
        "confidence": confidence,
        "attribution": attribution,
        "status": "classified"
    }

    write_log(entry)

    return jsonify({
        "content_id": content_id,
        "attribution": attribution,
        "llm_score": llm_score,
        "heuristic_score": heuristic_score,
        "confidence": confidence,
        "label": label
    })


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json()

    content_id = data.get("content_id")
    creator_id = data.get("creator_id")
    appeal_reason = data.get("appeal_reason")

    if not content_id or not creator_id or not appeal_reason:
        return jsonify({"error": "Missing content_id, creator_id, or appeal_reason"}), 400

    found = update_status(content_id, "pending_review", appeal_reason)

    if not found:
        return jsonify({"error": "content_id not found"}), 404

    appeal_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "appeal_submitted",
        "appeal_reason": appeal_reason,
        "status": "pending_review"
    }

    write_log(appeal_entry)

    return jsonify({
        "message": "Appeal received. Your submission has been flagged for human review.",
        "content_id": content_id,
        "status": "pending_review"
    })


@app.route("/log", methods=["GET"])
def log():
    return jsonify({"entries": get_log()})


if __name__ == "__main__":
    app.run(debug=True)