"""
Run this before starting the server to catch problems early:
  python check.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

ok = True

def chk(label, fn):
    global ok
    try:
        fn()
        print(f"  OK   {label}")
    except Exception as e:
        print(f"  FAIL {label}")
        print(f"       {e}")
        ok = False

print("\n── Checking dependencies ────────────────────────────────")
chk("fastapi",         lambda: __import__("fastapi"))
chk("uvicorn",         lambda: __import__("uvicorn"))
chk("pydantic",        lambda: __import__("pydantic"))
chk("langgraph",       lambda: __import__("langgraph"))
chk("langchain",       lambda: __import__("langchain"))
chk("langchain_openai",lambda: __import__("langchain_openai"))
chk("python-dotenv",   lambda: __import__("dotenv"))

print("\n── Checking project modules ─────────────────────────────")
chk("models.model",          lambda: __import__("models.model", fromlist=["gpt_model"]))
chk("schemas.scheme",        lambda: __import__("schemas.scheme", fromlist=["Swe"]))
chk("agents.intent_analyzer",lambda: __import__("agents.intent_analyzer", fromlist=["analyzer"]))
chk("agents.architect_agent",lambda: __import__("agents.architect_agent", fromlist=["archit"]))
chk("agents.planner",        lambda: __import__("agents.planner", fromlist=["agent_plan"]))
chk("agents.filebreak_agent",lambda: __import__("agents.filebreak_agent", fromlist=["file_break"]))
chk("agents.folder_create",  lambda: __import__("agents.folder_create", fromlist=["generate_files"]))
chk("agents.code_generator", lambda: __import__("agents.code_generator", fromlist=["code_generator"]))
chk("agents.docker_executor",lambda: __import__("agents.docker_executor", fromlist=["docker_executor"]))
chk("agents.debugger_agent", lambda: __import__("agents.debugger_agent", fromlist=["debugger"]))
chk("agents.test_generator", lambda: __import__("agents.test_generator", fromlist=["test_generator"]))
chk("agents.readme_generator",lambda: __import__("agents.readme_generator",fromlist=["readme_generator"]))
chk("agents.packager",       lambda: __import__("agents.packager", fromlist=["packager"]))
chk("main (graph build)",    lambda: __import__("main", fromlist=["build_graph"]))

print("\n── Checking environment ─────────────────────────────────")
from dotenv import load_dotenv; load_dotenv()
key = os.getenv("OPENAI_API_KEY","")
if key.startswith("sk-"):
    print(f"  OK   OPENAI_API_KEY found ({key[:8]}...)")
else:
    print("  FAIL OPENAI_API_KEY missing or invalid — add it to .env")
    ok = False

print("\n── Checking static files ────────────────────────────────")
chk("static/index.html", lambda: open("static/index.html").close())

print()
if ok:
    print("All checks passed.  Run:  uvicorn app:app --reload\n")
else:
    print("Fix the FAIL items above, then run:  uvicorn app:app --reload\n")
    sys.exit(1)
