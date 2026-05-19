import os
import zipfile
import shutil


def packager(state):
    """
    Zips the entire project directory into a downloadable .zip archive.
    The archive is placed one level above the project folder.
    """
    project_dir: str = state["project_dir"]
    project_name = os.path.basename(project_dir)
    zip_path = f"{project_dir}.zip"

    # Remove any previous zip
    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_dir):
            # Skip __pycache__ and .git
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            for fname in files:
                abs_path = os.path.join(root, fname)
                # Archive path keeps the project folder as root
                arc_name = os.path.join(
                    project_name,
                    os.path.relpath(abs_path, project_dir)
                )
                zf.write(abs_path, arc_name)

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"[packager] Created {zip_path} ({size_kb:.1f} KB)")

    return {
        "zip_path": zip_path,
        "status": "complete"
    }
