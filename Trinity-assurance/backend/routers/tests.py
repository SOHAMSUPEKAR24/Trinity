from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.models.schemas import (
    TestGenerationRequest,
    TestGenerationResponse,
    TestRunRequest,
    TestRunResponse,
)
from backend.services.test_generator import TestGenerator
from backend.services.test_runner import TestRunner
from backend.services.history_manager import TestHistory
from backend.utils.license_checker import is_license_valid
import os
import zipfile
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
generator = TestGenerator()  # API key auto-loaded from env


@router.post("/generate", response_model=TestGenerationResponse)
async def generate_tests(request: TestGenerationRequest):
    """
    Generate tests using AI for a given repository.
    Requires a valid license token.
    """
    # ✅ License verification
    if not is_license_valid(request.license_token):
        raise HTTPException(status_code=401, detail="Invalid or expired license token.")

    try:
        test_code = generator.generate_tests_from_repo(
            repo_url=request.repo_url,
            language=request.language,
            file_path=request.file_path,
            test_type=request.test_type,
            folder_filter=request.folder_filter,
            dry_run=request.dry_run
        )
        return TestGenerationResponse(status="success", generated_test_code=test_code)
    except Exception as e:
        logger.error(f"[TestOps] Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")


@router.post("/run", response_model=TestRunResponse)
def run_tests(request: TestRunRequest):
    """
    Run tests for the specified language and type.
    """
    try:
        runner = TestRunner(language=request.language, test_type=request.test_type)
        stdout, stderr = runner.run()

        return TestRunResponse(
            status="success" if not stderr else "error",
            output=stdout,
            error=stderr or None
        )
    except Exception as e:
        logger.error(f"[TestOps] Test run failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test run failed: {str(e)}")


@router.get("/history/{repo}", response_model=dict)
def get_test_history(repo: str):
    """
    Fetch AI-generated test history for a given repo.
    """
    try:
        history = TestHistory().fetch(repo)
        return {"repo": repo, "history": history}
    except Exception as e:
        logger.error(f"[TestOps] Failed to fetch history for {repo}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


@router.get("/download/{repo}")
def download_tests_zip(repo: str):
    """
    Download all tests for a given repo as a ZIP file.
    """
    folder_path = os.path.join("tests", repo)
    zip_path = f"{folder_path}.zip"

    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Test folder not found")

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        logger.info(f"[TestOps] ✅ Zipped tests for {repo} at {zip_path}")
    except Exception as e:
        logger.error(f"[TestOps] ❌ Failed to zip tests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to zip tests: {str(e)}")

    return FileResponse(
        path=zip_path,
        filename=f"{repo}_tests.zip",
        media_type="application/zip"
    )