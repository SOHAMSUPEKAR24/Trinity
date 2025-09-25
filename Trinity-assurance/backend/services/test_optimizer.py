import os
import logging
from backend.utils.git_ops import get_changed_files

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestOptimizer:
    def __init__(self, repo_path: str, language: str):
        self.repo_path = repo_path
        self.language = language.lower()

    def get_relevant_tests(self, test_dir: str = "tests/", src_dir: str = "src/") -> list:
        """
        Determine which test files are relevant based on the source code changes.
        """
        logger.info(f"[Trinity] 🔍 Analyzing repo for changed files: {self.repo_path}")
        changed_files = get_changed_files(self.repo_path)

        if not changed_files:
            logger.warning("[Trinity] ⚠️ No changed files found. Running all available tests.")
            return self._collect_all_tests(test_dir)

        relevant_tests = []

        for file in changed_files:
            if not self._is_valid_source_file(file):
                continue

            mapped = self._map_source_to_test(file, test_dir, src_dir)
            if mapped:
                relevant_tests.append(mapped)

        logger.info(f"[Trinity] 🧠 Optimized Test Selection: {relevant_tests}")
        return relevant_tests or self._collect_all_tests(test_dir)

    def _is_valid_source_file(self, file: str) -> bool:
        return file.endswith((".py", ".js", ".ts", ".java"))

    def _map_source_to_test(self, source_file: str, test_dir: str, src_dir: str) -> str:
        """
        Map a source file to its likely test file.
        Example:
          - src/utils/math.py => tests/test_math.py
          - src/api/user.ts => tests/test_user.ts
        """
        file_name = os.path.basename(source_file)
        test_name = ""

        if self.language == "python":
            test_name = f"test_{file_name}"
        elif self.language == "javascript":
            test_name = file_name.replace(".js", ".test.js")
        elif self.language == "typescript":
            test_name = file_name.replace(".ts", ".test.ts")
        elif self.language == "java":
            test_name = file_name.replace(".java", "Test.java")
        else:
            return None

        candidate_path = os.path.join(test_dir, test_name)
        full_candidate = os.path.join(self.repo_path, candidate_path)

        return candidate_path if os.path.exists(full_candidate) else None

    def _collect_all_tests(self, test_dir: str) -> list:
        """
        Fallback to collecting all test files when optimization isn't possible.
        """
        test_path = os.path.join(self.repo_path, test_dir)
        if not os.path.exists(test_path):
            logger.warning(f"[Trinity] 🚫 Test directory not found: {test_path}")
            return []

        return [
            os.path.join(test_dir, f)
            for f in os.listdir(test_path)
            if (
                f.startswith("test_")
                or f.endswith(".test.js")
                or f.endswith(".test.ts")
                or f.endswith("Test.java")
            )
        ]