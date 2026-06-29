import json
import os

LOG_FILE = "logs/audit.json"


def write_log(entry):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)


def get_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)


def update_status(content_id: str, new_status: str, appeal_reason: str) -> bool:
    """Updates an existing log entry's status. Returns True if found, False if not."""
    if not os.path.exists(LOG_FILE):
        return False

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    found = False
    for entry in logs:
        if entry.get("content_id") == content_id:
            entry["status"] = new_status
            entry["appeal_reason"] = appeal_reason
            found = True
            break

    if found:
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)

    return found