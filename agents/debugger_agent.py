import os
import re
from models.model import gpt_model

llm = gpt_model()

MAX_DEBUG_ATTEMPTS = 3


def _strip_fences(code: str) -> str:
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip())
    return code.strip()


def debugger(state):
    """
    Reads the execution errors, locates the offending file(s), and asks
    the LLM to produce a fix. Writes the fixed code back to disk.
    Tracks attempt count to prevent infinite loops.
    """
    errors: str = state.get("execution_errors", "")
    project_dir: str = state["project_dir"]
    attempts: int = state.get("debug_attempts", 0)

    if not errors.strip():
        return {"status": "execution_success", "debug_attempts": attempts}

    if attempts >= MAX_DEBUG_ATTEMPTS:
        print(f"[debugger] Max debug attempts ({MAX_DEBUG_ATTEMPTS}) reached.")
        return {"status": "debug_exhausted", "debug_attempts": attempts}

    # Collect all generated source files so the LLM has full context
    project_files: dict = state.get("generated_files", {})
    context_dump = "\n\n".join(
        f"### {path}\n{code}" for path, code in project_files.items()
    )

    prompt = f"""
You are a senior software engineer debugging a project.

The project failed with the following errors:
{errors}

Here is the full current codebase:
{context_dump}

Instructions:
1. Identify the root cause of each error.
2. Provide the complete fixed version of each affected file.
3. Format your response as a series of blocks, one per file:

FILE: <relative/path/to/file.py>
<complete fixed file content — no fences, no explanation>
END_FILE

Only include files you actually changed. Do not include unchanged files.
"""

    res = llm.invoke(prompt)
    raw = res.content.strip()

    # Parse the structured response
    pattern = r"FILE:\s*(.+?)\n(.*?)END_FILE"
    matches = re.findall(pattern, raw, re.DOTALL)

    fixed_files: dict = dict(project_files)
    patched = 0

    for rel_path, new_code in matches:
        rel_path = rel_path.strip()
        new_code = _strip_fences(new_code.strip())
        abs_path = os.path.join(project_dir, rel_path)

        if os.path.exists(os.path.dirname(abs_path)):
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_code)
            fixed_files[rel_path] = new_code
            patched += 1
            print(f"[debugger] Patched: {rel_path}")

    print(f"[debugger] Attempt {attempts + 1}: patched {patched} file(s).")

    return {
        "generated_files": fixed_files,
        "debug_attempts": attempts + 1,
        "status": "retrying_execution"
    }
