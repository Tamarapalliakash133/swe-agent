import subprocess
import os


MAX_TIMEOUT = 60  # seconds


def _has_dockerfile(project_dir: str) -> bool:
    return os.path.exists(os.path.join(project_dir, "Dockerfile"))


def _run_command(cmd: list[str], cwd: str, timeout: int = MAX_TIMEOUT) -> tuple[str, str, int]:
    """Run a shell command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s: {' '.join(cmd)}", 1
    except FileNotFoundError as e:
        return "", f"Command not found: {e}", 1


def docker_executor(state):
    """
    Attempts to build and run the project inside a Docker container.
    If Docker is unavailable, falls back to a lightweight local syntax check.
    """
    project_dir: str = state["project_dir"]
    project_name = os.path.basename(project_dir).lower().replace("_", "-")

    # ── Try Docker first ──────────────────────────────────────────────────────
    stdout, stderr, rc = _run_command(["docker", "info"], project_dir)

    if rc != 0 or not _has_dockerfile(project_dir):
        # Docker unavailable or no Dockerfile — do a local Python syntax check
        return _local_syntax_check(state, project_dir)

    print(f"[docker_executor] Building Docker image: {project_name}")
    build_out, build_err, build_rc = _run_command(
        ["docker", "build", "-t", project_name, "."],
        project_dir,
        timeout=120
    )

    if build_rc != 0:
        return {
            "execution_output": build_out,
            "execution_errors": build_err,
            "status": "execution_failed"
        }

    print(f"[docker_executor] Running container: {project_name}")
    run_out, run_err, run_rc = _run_command(
        ["docker", "run", "--rm", "--name", f"{project_name}-run",
         "-e", "TESTING=1", project_name],
        project_dir,
        timeout=MAX_TIMEOUT
    )

    status = "execution_success" if run_rc == 0 else "execution_failed"
    return {
        "execution_output": run_out,
        "execution_errors": run_err,
        "status": status
    }


def _local_syntax_check(state, project_dir: str) -> dict:
    """
    Fallback: run `python -m py_compile` on every .py file to catch
    syntax errors without Docker.
    """
    errors = []
    output_lines = []

    for root, _, files in os.walk(project_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            filepath = os.path.join(root, fname)
            rel = os.path.relpath(filepath, project_dir)
            out, err, rc = _run_command(
                ["python", "-m", "py_compile", filepath],
                project_dir
            )
            if rc == 0:
                output_lines.append(f"✓ {rel}")
            else:
                errors.append(f"✗ {rel}: {err.strip()}")

    if errors:
        return {
            "execution_output": "\n".join(output_lines),
            "execution_errors": "\n".join(errors),
            "status": "execution_failed"
        }

    return {
        "execution_output": "\n".join(output_lines) or "All files passed syntax check.",
        "execution_errors": "",
        "status": "execution_success"
    }
