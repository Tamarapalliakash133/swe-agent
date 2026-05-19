import os
from models.model import gpt_model

llm = gpt_model()


def readme_generator(state):
    """
    Generates a clean, developer-friendly README.md for the project.
    """
    project_dir: str = state["project_dir"]

    # Collect requirements.txt if it exists
    req_path = os.path.join(project_dir, "requirements.txt")
    requirements = ""
    if os.path.exists(req_path):
        requirements = open(req_path).read().strip()

    # Collect the file tree for display
    file_list = []
    for root, dirs, files in os.walk(project_dir):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        level = root.replace(project_dir, "").count(os.sep)
        indent = "  " * level
        folder_name = os.path.basename(root)
        if level == 0:
            file_list.append(f"{os.path.basename(project_dir)}/")
        else:
            file_list.append(f"{indent}{folder_name}/")
        subindent = "  " * (level + 1)
        for fname in sorted(files):
            file_list.append(f"{subindent}{fname}")

    tree = "\n".join(file_list)

    prompt = f"""
You are a technical writer creating a README.md for a software project.

Project: {state.get("user_request")}

Architecture overview:
{state.get("architect", "")}

File structure:
{tree}

Requirements:
{requirements}

Write a complete README.md with these sections:
1. Project title and one-line description.
2. Features — bullet list of what the project does.
3. Tech stack — what languages, frameworks, databases are used.
4. Project structure — show the file tree above formatted nicely.
5. Installation — step-by-step setup (clone, virtualenv, pip install, env vars).
6. Configuration — explain each .env variable.
7. Running the project — how to start the server or run the script.
8. Running tests — pytest command.
9. API reference (if applicable) — list each endpoint with method, path, description.
10. Docker usage (if applicable) — build and run commands.

Write in plain Markdown. Be concise but complete.
"""

    res = llm.invoke(prompt)
    readme = res.content.strip()

    readme_path = os.path.join(project_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print("[readme_generator] README.md written.")

    return {
        "readme": readme,
        "status": "readme_generated"
    }
