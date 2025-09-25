from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.get("/download/{repo_name}", response_class=FileResponse)
def download_zip(repo_name: str):
    """
    📦 Download the generated test suite as a ZIP file for a specific repo.
    """
    zip_path = os.path.join("tests", repo_name, f"{repo_name}.zip")

    if not os.path.exists(zip_path):
        logger.error(f"[Download] ❌ ZIP file not found at: {zip_path}")
        raise HTTPException(status_code=404, detail="ZIP file not found.")

    logger.info(f"[Download] ✅ Sending ZIP: {zip_path}")
    return FileResponse(
        path=zip_path,
        filename=f"{repo_name}_tests.zip",
        media_type="application/zip"
    )