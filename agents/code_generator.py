import os
import re
from models.model import gpt_model

llm = gpt_model()


def _get_all_project_files(project_dir: str) -> list[str]:
    """Walk the project directory and return all non-placeholder file paths."""
    paths = []
    for root, _, files in os.walk(project_dir):
        for fname in files:
            if fname == "__init__.py":
                continue
            paths.append(os.path.join(root, fname))
    return sorted(paths)


def _relative_path(project_dir: str, filepath: str) -> str:
    return os.path.relpath(filepath, project_dir)


def _strip_fences(code: str) -> str:
    """Remove markdown code fences that the model might add."""
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip())
    return code.strip()


def code_generator(state):
    """
    Iterates over every file in the project directory and asks the LLM
    to write production-ready code for it, given full project context.
    """
    project_dir: str = state["project_dir"]
    all_files = _get_all_project_files(project_dir)

    # Build a manifest string so the LLM understands the full project shape
    manifest = "\n".join(
        _relative_path(project_dir, fp) for fp in all_files
    )

    generated: dict = {}

    for filepath in all_files:
        rel = _relative_path(project_dir, filepath)
        ext = os.path.splitext(filepath)[1]

        prompt = f"""
You are an expert software engineer writing production-ready code.

Project request: {state["user_request"]}

Architecture decisions:
{state["architect"]}

Implementation plan:
{state["tasks"]}

Full project file manifest:
{manifest}

You are now writing the file: {rel}

Rules:
- Write complete, working code. No placeholders, no TODOs, no ellipses.
- Follow best practices for the language/framework being used.
- Import only from files that exist in the manifest above.
- For requirements.txt: list one package per line, pinned versions where sensible.
- For Dockerfile: write a minimal, production-appropriate image.
- For .env.example: list all required env vars with descriptive placeholder values.
- For README.md: write setup + run instructions.
- Do NOT wrap your output in markdown code fences.
- Output ONLY the file content, nothing else.
"""

        res = llm.invoke(prompt)
        code = _strip_fences(res.content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        generated[rel] = code
        print(f"[code_generator] Written: {rel}")

    return {
        "generated_files": generated,
        "status": "code_generated"
    }
