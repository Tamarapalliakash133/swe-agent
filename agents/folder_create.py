import os
import json


def generate_files(state):
    """
    Creates the project folder structure on disk based on the file tree
    produced by filebreak_agent. Populates each file with a placeholder
    so downstream code_generator knows exactly which paths to fill.
    """
    file_tree: dict = state.get("file_tree", {})
    user_request: str = state.get("user_request", "project")

    # Derive a safe project name from the request
    project_name = (
        user_request.lower()
        .replace(" ", "_")
        .replace("/", "_")
        [:40]
    )
    project_dir = os.path.join("/tmp", project_name)
    os.makedirs(project_dir, exist_ok=True)

    created = []

    for folder, files in file_tree.items():
        if folder == "root":
            target_dir = project_dir
        else:
            target_dir = os.path.join(project_dir, folder)
            os.makedirs(target_dir, exist_ok=True)

            # Drop an __init__.py in every Python package folder
            init_path = os.path.join(target_dir, "__init__.py")
            if not os.path.exists(init_path):
                open(init_path, "w").close()

        for filename in files:
            filepath = os.path.join(target_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {filename} — to be generated\n")
            created.append(filepath)

    print(f"[folder_create] Created {len(created)} files under {project_dir}")

    return {
        "project_dir": project_dir,
        "status": "structure_created"
    }
