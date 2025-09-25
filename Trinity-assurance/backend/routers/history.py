from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
import os
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HISTORY_BASE_DIR = "tests/.history"

@router.get("/{repo_name}", response_class=JSONResponse)
def get_test_history(
    repo_name: str = Path(..., description="Sanitized repo name (used internally)")
):
    """
    Returns AI-generated test history for a given repo.
    """
    repo_dir = os.path.join(HISTORY_BASE_DIR, repo_name)

    if not os.path.isdir(repo_dir):
        logger.warning(f"[History] No history found at: {repo_dir}")
        raise HTTPException(status_code=404, detail=f"No history found for repo '{repo_name}'.")

    history = []

    for filename in os.listdir(repo_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(repo_dir, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    history.append({
                        "file": data.get("file", filename),
                        "language": data.get("language", ""),
                        "test_type": data.get("test_type", "auto"),
                        "output_path": data.get("output_path", ""),
                        "ai_output": data.get("ai_output", "")
                    })
            except Exception as e:
                logger.error(f"[History] Error loading {file_path}: {e}")
                continue

    return {"repo": repo_name, "history": history}