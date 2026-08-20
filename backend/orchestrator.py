"""Runs the full ingestion -> cleaning -> scoring -> newsletter pipeline
end-to-end and persists the result to Supabase."""
from __future__ import annotations

from backend.db.supabase_client import save_run
from backend.models.schemas import NewsletterRun
from backend.pipeline.credibility import tag_credibility
from backend.pipeline.dedup import deduplicate
from backend.pipeline.ingest import SEARCH_QUERIES, run_ingestion
from backend.pipeline.newsletter import draft_newsletter
from backend.pipeline.relevance import score_relevance


def run_pipeline() -> NewsletterRun:
    run = NewsletterRun(query_set=SEARCH_QUERIES, status="running")

    try:
        raw_articles = run_ingestion(queries=SEARCH_QUERIES)
        tag_credibility(raw_articles)
        deduped = deduplicate(raw_articles)
        relevant = score_relevance(deduped)
        markdown, sections = draft_newsletter(relevant)

        run.raw_articles = raw_articles
        run.deduped_count = len(deduped)
        run.relevant_articles = relevant
        run.newsletter_markdown = markdown
        run.newsletter_sections = sections
        run.status = "success"
    except Exception as exc:  # noqa: BLE001 - surface any failure on the run record
        run.status = "failed"
        run.error = str(exc)

    return save_run(run)
