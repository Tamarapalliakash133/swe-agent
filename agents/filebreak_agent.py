from models.model import gpt_model
import json
import re

llm = gpt_model()


def file_break(state):
    prompt = f"""
    You are a software architect mapping implementation tasks to project files.

    Tasks:
    {state["tasks"]}

    Architecture context:
    {state["architect"]}

    Group the tasks by folder. Each key is a folder name, each value is a list of filenames that belong there.
    Always include a root-level entry for files like main.py, requirements.txt, Dockerfile, .env.example.

    Rules:
    - Return ONLY valid JSON. No markdown, no explanation, no code fences.
    - Use double quotes for all keys and string values.
    - Output must start with {{ and end with }}.

    Example output:
    {{
        "root": ["main.py", "requirements.txt", "Dockerfile", ".env.example"],
        "models": ["user.py", "post.py"],
        "routes": ["auth.py", "posts.py"],
        "services": ["auth_service.py", "database.py"],
        "config": ["database.py", "settings.py"],
        "tests": ["test_auth.py", "test_posts.py"]
    }}
    """

    res = llm.invoke(prompt)
    raw = res.content.strip()

    # Strip any accidental markdown fences
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"```$", "", raw).strip()

    try:
        file_tree = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback to a sane default so the pipeline doesn't break
        file_tree = {
            "root": ["main.py", "requirements.txt", "Dockerfile", ".env.example"],
            "models": ["model.py"],
            "routes": ["routes.py"],
            "services": ["service.py"],
            "tests": ["test_main.py"]
        }

    return {
        "filebreak": raw,
        "file_tree": file_tree
    }
