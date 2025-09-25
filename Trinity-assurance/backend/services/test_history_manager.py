import os
import json
from datetime import datetime
from typing import List, Dict

HISTORY_BASE_DIR = os.path.join("tests", "_history")
os.makedirs(HISTORY_BASE_DIR, exist_ok=True)

def _sanitize_repo_name(repo: str) -> str:
    return repo.replace("/", "_").replace("\\", "_").replace(" ", "_")

def save_test_result(repo: str, test_code: str, result: Dict) -> None:
    """
    Save the generated test code and its result to a timestamped JSON file.
    Location: /tests/_history/{repo}/{timestamp}.json
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_repo = _sanitize_repo_name(repo)
    repo_dir = os.path.join(HISTORY_BASE_DIR, safe_repo)
    os.makedirs(repo_dir, exist_ok=True)

    history_entry = {
        "timestamp": timestamp,
        "repo": repo,
        "test_code": test_code,
        "result": result
    }

    file_path = os.path.join(repo_dir, f"{timestamp}.json")
    try:
        with open(file_path, "w") as f:
            json.dump(history_entry, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save test history: {e}")

def load_test_history(repo: str) -> List[Dict]:
    """
    Load test history for a given repo, sorted by newest first.
    Returns a list of test records.
    """
    safe_repo = _sanitize_repo_name(repo)
    repo_dir = os.path.join(HISTORY_BASE_DIR, safe_repo)

    if not os.path.exists(repo_dir):
        return []

    history = []
    try:
        for file_name in sorted(os.listdir(repo_dir), reverse=True):
            if file_name.endswith(".json"):
                file_path = os.path.join(repo_dir, file_name)
                with open(file_path, "r") as f:
                    history.append(json.load(f))
    except Exception as e:
        print(f"⚠️ Failed to load some history entries: {e}")

    return history