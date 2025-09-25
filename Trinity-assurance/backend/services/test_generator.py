# backend/services/test_generator.py

import os
import re
import zipfile
import logging
from typing import List

from dotenv import load_dotenv
from groq import Groq

from backend.utils.git_ops import clone_or_pull_repo
from backend.utils.prompts import TEST_GEN_PROMPT_TEMPLATE
from backend.services.history_manager import TestHistory

# ──────────────────────────────────────────────────────────────────────────────
# Env loading: read .env from project root (…/Trinity-assurance/.env)
# file is at backend/services/test_generator.py → go up two levels to root
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TestGenerator:
    def __init__(self, api_key: str | None = None, model: str = "llama3-8b-8192"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required (set it in your root .env)")

        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.history = TestHistory()

    # ──────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────
    def sanitize_filename(self, name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)

    def get_all_source_files(self, repo_path: str, language: str, folder_filter: str = "") -> List[str]:
        ext = {
            "python": ".py",
            "java": ".java",
            "javascript": ".js",
            "typescript": ".ts",
        }.get(language, ".txt")

        valid_files: List[str] = []
        for root, dirs, files in os.walk(repo_path):
            # ignore hidden folders and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            if folder_filter and folder_filter not in root:
                continue

            for file in files:
                if file.endswith(ext) and not file.startswith("."):
                    full_path = os.path.join(root, file)
                    logger.info(f"[Scanner] ✅ Found: {full_path}")
                    valid_files.append(full_path)

        logger.info(f"[Scanner] Total valid source files: {len(valid_files)}")
        return valid_files

    def clean_test_code(self, code: str) -> str:
        code = code.strip()
        if code.startswith("```"):
            parts = code.split("```")
            return parts[1].strip() if len(parts) > 1 else code.replace("```", "").strip()
        return code

    def prepend_import_if_needed(self, source_file: str, repo_path: str, language: str, test_code: str) -> str:
        """Best-effort import fixer for Python tests to avoid NameError."""
        if language != "python":
            return test_code

        rel_path = os.path.relpath(source_file, repo_path)
        module_path = os.path.splitext(rel_path)[0].replace(os.sep, ".").replace("-", "_")

        # Only add import if the target isn't itself a test file
        if "test_" not in os.path.basename(source_file).lower():
            return f"from {module_path} import *\n\n{test_code}"
        return test_code

    # ──────────────────────────────────────────────────────────────────────
    # Core entry
    # ──────────────────────────────────────────────────────────────────────
    def generate_tests_from_repo(
        self,
        repo_url: str,
        language: str,
        file_path: str = "",
        folder_filter: str = "",
        dry_run: bool = False,
        test_type: str = "auto",
    ) -> str:
        logger.info(f"[Trinity] Cloning repo: {repo_url}")
        repo_path = clone_or_pull_repo(repo_url)
        repo_name = os.path.basename(repo_path).replace("-", "_")

        # Per-repo test folder
        test_folder = os.path.join("tests", repo_name)
        os.makedirs(test_folder, exist_ok=True)

        ext = {"python": "py", "java": "java", "javascript": "js", "typescript": "ts"}.get(language, "txt")

        files_to_process = [file_path] if file_path else self.get_all_source_files(
            repo_path, language, folder_filter
        )

        if not files_to_process:
            logger.error(f"[Trinity] ❌ No source files found in: {repo_path}")
            return "No source files found to generate tests."

        combined_test_output = ""
        test_file_paths: List[str] = []

        for source_file in files_to_process:
            try:
                with open(source_file, "r", encoding="utf-8", errors="ignore") as f:
                    source_code = f.read()
            except Exception as e:
                logger.error(f"❌ Failed to read {source_file}: {e}")
                continue

            prompt = TEST_GEN_PROMPT_TEMPLATE.format(language=language, diff=source_code)

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=1000,
                )
                raw_code = response.choices[0].message.content
                test_code = self.clean_test_code(raw_code)
                test_code = self.prepend_import_if_needed(source_file, repo_path, language, test_code)

                safe_name = self.sanitize_filename(
                    os.path.relpath(source_file, repo_path).replace(f".{ext}", "")
                )
                test_file_name = f"test_{safe_name}.{ext}"
                test_file_path = os.path.join(test_folder, test_file_name)

                if not dry_run:
                    with open(test_file_path, "w", encoding="utf-8") as f:
                        f.write(test_code)
                    test_file_paths.append(test_file_path)

                    # Save to test history
                    self.history.save(
                        repo=repo_name,
                        file=source_file,
                        language=language,
                        test_type=test_type,
                        output_path=test_file_path,
                        ai_output=test_code,
                    )
                    logger.info(f"[Trinity] ✅ Test saved: {test_file_path}")
                else:
                    logger.info(f"[Trinity] 🧪 Dry run: skipped writing {test_file_name}")

                combined_test_output += f"\n\n==== {test_file_name} ====\n{test_code}"

            except Exception as e:
                logger.error(f"❌ Error generating test for {source_file}: {e}")
                continue

        # ZIP packaging → per-repo path: tests/<repo>/<repo>.zip
        if not dry_run and test_file_paths:
            zip_path = os.path.join("tests", repo_name, f"{repo_name}.zip")
            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for path in test_file_paths:
                        arcname = os.path.relpath(path, test_folder)
                        zipf.write(path, arcname)
                logger.info(f"[Trinity] 📦 All tests zipped: {zip_path}")
            except Exception as e:
                logger.error(f"[Trinity] ❌ Failed to create ZIP: {e}")

        return combined_test_output.strip() or "Test generation completed, but no tests were generated."