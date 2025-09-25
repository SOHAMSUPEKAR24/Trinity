# backend/utils/prompts.py

TEST_GEN_PROMPT_TEMPLATE = """
You are a highly skilled senior QA automation engineer. Your task is to generate **robust, production-quality test code** for the following source file written in **{language}**.

========================
SOURCE CODE:
{diff}
========================

Your Responsibilities:
1. Identify functions, classes, and logic in the above code.
2. Generate unit or integration tests that validate:
   - Correct functionality
   - Edge cases
   - Exception handling
   - Boundary conditions
   - Invalid input scenarios
3. Use **standard frameworks** for {language}:
   - PyTest for Python
   - JUnit/TestNG for Java
   - Jest/Playwright/Cypress for JavaScript/TypeScript
   - Add appropriate `@Test`, `describe`, or `test` annotations or structures.
4. Include all **necessary imports**, mocks, and setup/teardown if needed.
5. ⚠️ Do NOT describe anything. Just return raw, executable test code as a single file.
6. The test should be ready to run **immediately**, with no missing dependencies or placeholders.
7. Avoid unnecessary comments. Keep it clean and minimal.
8. Ensure method/function coverage is high.

🔁 Output Format:
✅ Return a complete test file as plain code. No markdown, no explanations, and no wrapping text.

Make the output intelligent, professional, and efficient.
"""