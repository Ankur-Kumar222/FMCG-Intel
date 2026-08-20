from __future__ import annotations

import os
from functools import lru_cache

from supabase import Client, create_client

from backend.models.schemas import NewsletterRun

TABLE = "newsletter_runs"


@lru_cache
def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)


def save_run(run: NewsletterRun) -> NewsletterRun:
    client = get_client()
    row = {
        "query_set": run.query_set,
        "raw_articles": [a.model_dump(mode="json") for a in run.raw_articles],
        "deduped_count": run.deduped_count,
        "relevant_articles": [a.model_dump(mode="json") for a in run.relevant_articles],
        "newsletter_markdown": run.newsletter_markdown,
        "newsletter_sections": [s.model_dump(mode="json") for s in run.newsletter_sections],
        "status": run.status,
        "error": run.error,
    }
    response = client.table(TABLE).insert(row).execute()
    saved = response.data[0]
    return _row_to_run(saved)


def get_latest_run() -> NewsletterRun | None:
    client = get_client()
    response = (
        client.table(TABLE)
        .select("*")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_run(response.data[0])


def get_run(run_id: str) -> NewsletterRun | None:
    client = get_client()
    response = client.table(TABLE).select("*").eq("id", run_id).limit(1).execute()
    if not response.data:
        return None
    return _row_to_run(response.data[0])


def _row_to_run(row: dict) -> NewsletterRun:
    return NewsletterRun(**row)
