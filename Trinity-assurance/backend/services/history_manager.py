import os
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestHistory:
    def __init__(self, base_dir: str = "tests"):
        self.base_dir = base_dir
        self.history_dir = os.path.join(self.base_dir, ".history")
        os.makedirs(self.history_dir, exist_ok=True)

    def sanitize_repo(self, repo: str) -> str:
        return repo.replace("/", "_").replace("-", "_")

    def save(self, repo: str, file: str, language: str, test_type: str, output_path: str, ai_output: str):
        repo_sanitized = self.sanitize_repo(repo)
        history_path = os.path.join(self.history_dir, f"{repo_sanitized}.json")

        record = {
            "file": file,
            "language": language,
            "test_type": test_type,
            "output_path": output_path,
            "ai_output": ai_output
        }

        history = []
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    history = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"[Trinity] Corrupt history file. Starting fresh: {history_path}")
                history = []

        history.append(record)

        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)
        logger.info(f"[Trinity] ✅ History saved for: {file}")

    def fetch(self, repo: str):
        repo_sanitized = self.sanitize_repo(repo)
        history_path = os.path.join(self.history_dir, f"{repo_sanitized}.json")

        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"[Trinity] ❌ Failed to decode history file: {history_path}")
                return []

        logger.warning(f"[Trinity] ⚠️ No history file found for repo: {repo}")
        return []