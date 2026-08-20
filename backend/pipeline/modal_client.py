"""Thin client for the Modal-hosted LLM endpoint.

The model is served via Modal's built-in Endpoints product (SGLang), which
exposes an OpenAI-compatible /v1/chat/completions API and requires a bearer
proxy token for auth.
"""
from __future__ import annotations

import json
import os
import re

import httpx

MODAL_TIMEOUT_SECONDS = 120


def _base_url() -> str:
    url = os.environ.get("MODAL_LLM_ENDPOINT_URL")
    if not url:
        raise RuntimeError("MODAL_LLM_ENDPOINT_URL is not set")
    return url.rstrip("/")


def _model_name() -> str:
    return os.environ.get("MODAL_MODEL_NAME", "Qwen/Qwen3.8-27B")


def _headers() -> dict:
    token = os.environ.get("MODAL_API_TOKEN")
    if not token:
        raise RuntimeError("MODAL_API_TOKEN is not set")
    return {"Authorization": f"Bearer {token}"}


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
    # models occasionally add stray commentary around the JSON object -- grab
    # the outermost {...} block if the raw text isn't valid JSON on its own.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def chat_json(system_prompt: str, user_content: str, max_tokens: int = 4096) -> dict:
    """Call the OpenAI-compatible chat completions endpoint and parse the
    assistant's reply as JSON."""
    response = httpx.post(
        f"{_base_url()}/v1/chat/completions",
        headers=_headers(),
        json={
            "model": _model_name(),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
            # Qwen3 is a reasoning model that otherwise burns the token budget
            # on a separate `reasoning_content` field and can leave `content`
            # empty; we only ever parse `content`, so thinking mode is off.
            "chat_template_kwargs": {"enable_thinking": False},
        },
        timeout=MODAL_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    body = response.json()
    content = body["choices"][0]["message"]["content"]
    finish_reason = body["choices"][0].get("finish_reason")
    try:
        return _extract_json(content)
    except json.JSONDecodeError as exc:
        hint = " (response was truncated by max_tokens -- raise max_tokens or shrink the input)" if finish_reason == "length" else ""
        raise ValueError(f"Model did not return valid JSON{hint}: {exc}. Raw content: {content[:500]!r}") from exc
