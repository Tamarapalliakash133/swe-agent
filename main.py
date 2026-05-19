from langgraph.graph import StateGraph, END
from typing import TypedDict, Any

from agents.intent_analyzer import analyzer
from agents.architect_agent import archit
from agents.planner import agent_plan
from agents.filebreak_agent import file_break
from agents.folder_create import generate_files
from agents.code_generator import code_generator
from agents.docker_executor import docker_executor
from agents.debugger_agent import debugger, MAX_DEBUG_ATTEMPTS
from agents.test_generator import test_generator
from agents.readme_generator import readme_generator
from agents.packager import packager


# ── State definition ─────────────────────────────────────────────────────────

class SweState(TypedDict, total=False):
    user_request: str
    intent_analyze: str
    architect: str
    plan: str
    tasks: str
    filebreak: str
    file_tree: dict
    generated_files: dict
    project_dir: str
    execution_output: str
    execution_errors: str
    debug_attempts: int
    test_code: dict
    readme: str
    zip_path: str
    status: str


# ── Routing logic ─────────────────────────────────────────────────────────────

def route_after_execution(state: SweState) -> str:
    """Decide whether to debug, move on, or give up after Docker execution."""
    status = state.get("status", "")
    errors = state.get("execution_errors", "").strip()
    attempts = state.get("debug_attempts", 0)

    if status == "execution_success" or not errors:
        return "test_generator"

    if attempts >= MAX_DEBUG_ATTEMPTS:
        # Too many failures — skip to tests anyway so we still deliver output
        print(f"[graph] Debug limit reached, proceeding to tests.")
        return "test_generator"

    return "debugger"


def route_after_debug(state: SweState) -> str:
    """After a debug patch, re-run execution."""
    status = state.get("status", "")
    if status == "debug_exhausted":
        return "test_generator"
    return "docker_executor"


# ── Graph assembly ────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(SweState)

    # Register all nodes
    graph.add_node("intent_analyzer", analyzer)
    graph.add_node("architect",       archit)
    graph.add_node("planner",         agent_plan)
    graph.add_node("file_break",      file_break)
    graph.add_node("folder_create",   generate_files)
    graph.add_node("code_generator",  code_generator)
    graph.add_node("docker_executor", docker_executor)
    graph.add_node("debugger",        debugger)
    graph.add_node("test_generator",  test_generator)
    graph.add_node("readme_generator",readme_generator)
    graph.add_node("packager",        packager)

    # Linear edges
    graph.set_entry_point("intent_analyzer")
    graph.add_edge("intent_analyzer", "architect")
    graph.add_edge("architect",       "planner")
    graph.add_edge("planner",         "file_break")
    graph.add_edge("file_break",      "folder_create")
    graph.add_edge("folder_create",   "code_generator")
    graph.add_edge("code_generator",  "docker_executor")

    # Conditional: execution → debug loop or tests
    graph.add_conditional_edges(
        "docker_executor",
        route_after_execution,
        {
            "debugger":       "debugger",
            "test_generator": "test_generator",
        }
    )

    # Conditional: after debug, re-run execution or skip to tests
    graph.add_conditional_edges(
        "debugger",
        route_after_debug,
        {
            "docker_executor": "docker_executor",
            "test_generator":  "test_generator",
        }
    )

    graph.add_edge("test_generator",   "readme_generator")
    graph.add_edge("readme_generator", "packager")
    graph.add_edge("packager",         END)

    return graph.compile()


# ── Entry point ───────────────────────────────────────────────────────────────

def run_swe_agent(user_request: str) -> dict:
    """
    Run the full autonomous SWE pipeline for a given natural language request.

    Args:
        user_request: e.g. "Build a FastAPI blog API with JWT auth and PostgreSQL"

    Returns:
        Final state dict including zip_path for download.
    """
    graph = build_graph()

    initial_state: SweState = {
        "user_request":     user_request,
        "intent_analyze":   "",
        "architect":        "",
        "plan":             "",
        "tasks":            "",
        "filebreak":        "",
        "file_tree":        {},
        "generated_files":  {},
        "project_dir":      "",
        "execution_output": "",
        "execution_errors": "",
        "debug_attempts":   0,
        "test_code":        {},
        "readme":           "",
        "zip_path":         "",
        "status":           "pending",
    }

    print(f"\n{'='*60}")
    print(f"SWE Agent starting: {user_request}")
    print(f"{'='*60}\n")

    final_state = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"Done! Project at: {final_state.get('project_dir')}")
    print(f"Download:         {final_state.get('zip_path')}")
    print(f"{'='*60}\n")

    return final_state


if __name__ == "__main__":
    import sys
    request = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "Build a FastAPI blog API with JWT authentication and PostgreSQL"
    result = run_swe_agent(request)
    print(f"Zip ready: {result.get('zip_path')}")
