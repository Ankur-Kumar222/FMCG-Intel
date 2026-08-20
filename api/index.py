"""FastAPI app -- deployed on Vercel as a Python serverless function.

Vercel's Python builder detects this module's `app` (an ASGI application)
and serves every route under it as a serverless function.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.db.supabase_client import get_latest_run, get_run
from backend.orchestrator import run_pipeline
from backend.pipeline.export import MIME_TYPES, export_run
from backend.pipeline.modal_client import check_status

app = FastAPI(title="FMCG Deal Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/modal-status")
def modal_status():
    return check_status()


@app.post("/api/generate")
def generate():
    return run_pipeline()


@app.get("/api/latest")
def latest():
    run = get_latest_run()
    if run is None:
        raise HTTPException(status_code=404, detail="No runs yet")
    return run


@app.get("/api/runs/{run_id}/export")
def export(run_id: str, format: str = "json"):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if format not in MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    content = export_run(run, format)
    filename = f"fmcg-newsletter-{run_id}.{format}"
    return Response(
        content=content,
        media_type=MIME_TYPES[format],
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
