import os
import sys
import logging
import traceback
import importlib.util
import subprocess
from typing import Tuple
from backend.services.history_manager import TestHistory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestRunner:
    def __init__(self, language: str = "python", test_type: str = "unit"):
        self.language = language.lower()
        self.test_type = test_type.lower()
        self.history = TestHistory()

    def run(self) -> Tuple[str, str]:
        logger.info(f"[Trinity] 🚀 Running {self.test_type} tests for language: {self.language}")

        try:
            if self.language == "python":
                stdout, stderr = self._run_python_tests()
            elif self.language == "java":
                stdout, stderr = self._run_java_tests()
            elif self.language == "javascript":
                stdout, stderr = self._run_js_tests()
            else:
                return "", f"❌ Unsupported language: {self.language}"

            self.history.save(
                repo="latest_run",
                file="*",
                language=self.language,
                test_type=self.test_type,
                output_path="N/A",
                ai_output=stdout + "\n\n" + stderr
            )

            return stdout, stderr

        except Exception as e:
            error_msg = f"[Trinity] Test execution failed: {str(e)}"
            logger.error(error_msg)
            return "", error_msg

    def _run_python_tests(self) -> Tuple[str, str]:
        logger.info("[Trinity] 🧪 Executing Python tests using dynamic import...")

        test_dir = "tests"
        output = ""
        errors = ""

        if not os.path.exists(test_dir):
            return "", "❌ No 'tests/' directory found."

        # Add both CWD and 'repos' folder to sys.path for import resolution
        sys.path.insert(0, os.path.abspath("repos"))
        sys.path.insert(0, os.getcwd())

        try:
            for root, _, files in os.walk(test_dir):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        try:
                            spec = importlib.util.spec_from_file_location("test_module", file_path)
                            test_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(test_module)
                            output += f"✅ Ran test: {file_path}\n"
                        except Exception:
                            error_trace = traceback.format_exc()
                            errors += f"❌ Error in {file_path}:\n{error_trace}\n"
        finally:
            # Clean up sys.path
            if os.getcwd() in sys.path:
                sys.path.remove(os.getcwd())
            if os.path.abspath("repos") in sys.path:
                sys.path.remove(os.path.abspath("repos"))

        return output.strip(), errors.strip()

    def _run_java_tests(self) -> Tuple[str, str]:
        logger.info("[Trinity] 🧪 Compiling and executing Java tests...")

        try:
            java_test_dir = "tests"
            java_files = [os.path.join(java_test_dir, f) for f in os.listdir(java_test_dir) if f.endswith(".java")]

            if not java_files:
                return "", "❌ No Java test files found in 'tests/'"

            compile = subprocess.run(
                ["javac"] + java_files,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if compile.returncode != 0:
                return compile.stdout, compile.stderr

            output = ""
            for file in java_files:
                classname = os.path.splitext(os.path.basename(file))[0]
                run = subprocess.run(
                    ["java", "-cp", java_test_dir, classname],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                output += f"\n\n=== Running {classname}.java ===\n"
                output += run.stdout + run.stderr

            return output.strip(), ""

        except Exception as e:
            return "", f"Java test error: {str(e)}"

    def _run_js_tests(self) -> Tuple[str, str]:
        logger.info("[Trinity] 🧪 Running JavaScript tests via npm...")

        try:
            result = subprocess.run(
                ["npm", "test"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", f"JavaScript test error: {str(e)}"