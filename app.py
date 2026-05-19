import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(
    title="Autonomous SWE Agent",
    description="Converts natural language requirements into downloadable software projects.",
    version="1.0.0"
)

# Serve the static folder (index.html, css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory job store  (swap for Redis in production)
jobs: dict = {}


class GenerateRequest(BaseModel):
    request: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    zip_path: str | None = None
    error: str | None = None


def _run_job(job_id: str, user_request: str):
    """Runs in a background thread — imports are lazy so startup never fails."""
    try:
        jobs[job_id]["status"] = "running"

        # Lazy import: only happens when a job is actually kicked off
        from main import run_swe_agent
        result = run_swe_agent(user_request)

        jobs[job_id]["status"] = result.get("status", "complete")
        jobs[job_id]["zip_path"] = result.get("zip_path")
        jobs[job_id]["result"] = result
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        print(f"[job {job_id}] ERROR: {e}")


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/", methods = ["GET","HEAD"])
async def index():
    return FileResponse("static/index.html")


# ── API ───────────────────────────────────────────────────────────────────────

@app.post("/generate", response_model=JobStatus)
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "queued", "zip_path": None, "error": None}
    background_tasks.add_task(_run_job, job_id, req.request)
    return JobStatus(job_id=job_id, status="queued")


@app.get("/status/{job_id}", response_model=JobStatus)
async def status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        zip_path=job.get("zip_path"),
        error=job.get("error")
    )


@app.get("/download/{job_id}")
async def download(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    if job["status"] not in ("complete", "tests_generated", "readme_generated"):
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready. Current status: {job['status']}"
        )

    zip_path = job.get("zip_path")
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Zip file not found on disk.")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=os.path.basename(zip_path)
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)