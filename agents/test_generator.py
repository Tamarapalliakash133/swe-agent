import os
import re
from models.model import gpt_model

llm = gpt_model()


def _strip_fences(code: str) -> str:
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip())
    return code.strip()


def test_generator(state):
    """
    Generates pytest-based test files for each non-test source file.
    Writes them into the tests/ folder of the project.
    """
    project_dir: str = state["project_dir"]
    generated_files: dict = state.get("generated_files", {})
    tests_dir = os.path.join(project_dir, "tests")
    os.makedirs(tests_dir, exist_ok=True)

    # Write __init__.py if missing
    init = os.path.join(tests_dir, "__init__.py")
    if not os.path.exists(init):
        open(init, "w").close()

    # Only generate tests for non-test Python source files
    source_files = {
        path: code for path, code in generated_files.items()
        if path.endswith(".py")
        and not path.startswith("tests/")
        and os.path.basename(path) not in ("__init__.py", "main.py")
    }

    test_code: dict = {}

    for rel_path, source in source_files.items():
        module_name = os.path.splitext(os.path.basename(rel_path))[0]
        test_filename = f"test_{module_name}.py"
        test_path = os.path.join(tests_dir, test_filename)

        # Skip if a real test file already exists (written by code_generator)
        if os.path.exists(test_path):
            existing = open(test_path, encoding="utf-8").read().strip()
            if existing and "to be generated" not in existing:
                test_code[f"tests/{test_filename}"] = existing
                continue

        prompt = f"""
You are a senior software engineer writing pytest unit tests.

Project context:
{state.get("user_request", "")}

Source file being tested ({rel_path}):
{source}

Write comprehensive pytest unit tests for this file. Include:
- Happy path tests for every public function/class method.
- Edge cases and error handling tests where relevant.
- Use mocking (unittest.mock) for external dependencies (DB, HTTP, etc.).
- Tests should be self-contained and not require a running server or database.

Rules:
- Output ONLY the test file content. No explanation, no fences.
- Use pytest style (not unittest.TestCase).
- Import the module using its dotted path relative to the project root.
"""

        res = llm.invoke(prompt)
        code = _strip_fences(res.content)

        with open(test_path, "w", encoding="utf-8") as f:
            f.write(code)

        test_code[f"tests/{test_filename}"] = code
        print(f"[test_generator] Written: tests/{test_filename}")

    return {
        "test_code": test_code,
        "status": "tests_generated"
    }
