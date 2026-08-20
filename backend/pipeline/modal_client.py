"""Thin HTTP client for the Modal-hosted LLM web endpoint (modal_app/llm_service.py)."""
from __future__ import annotations

import json
import os

import httpx

MODAL_TIMEOUT_SECONDS = 40


def _endpoint_url() -> str:
    url = os.environ.get("MODAL_LLM_ENDPOINT_URL")
    if not url:
        raise RuntimeError("MODAL_LLM_ENDPOINT_URL is not set")
    return url


def infer(task: str, payload: dict) -> dict:
    """Call the Modal endpoint with a task name ('score_relevance' | 'draft_newsletter')
    and a JSON-serializable payload. Returns the parsed JSON response body."""
    response = httpx.post(
        _endpoint_url(),
        json={"task": task, "payload": payload},
        timeout=MODAL_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
