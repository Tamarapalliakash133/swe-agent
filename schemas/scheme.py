from pydantic import BaseModel
from typing import Optional


class Swe(BaseModel):
    user_request: str = ""
    intent_analyze: str = ""
    architect: str = ""
    plan: str = ""
    tasks: str = ""
    filebreak: str = ""
    file_tree: dict = {}
    generated_files: dict = {}
    project_dir: str = ""
    execution_output: str = ""
    execution_errors: str = ""
    debug_attempts: int = 0
    test_code: dict = {}
    readme: str = ""
    zip_path: str = ""
    status: str = "pending"
