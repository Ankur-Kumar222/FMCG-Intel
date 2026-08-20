"""Newsletter drafting: one Modal LLM call turns the deduped, relevant,
credibility-tagged article set into a structured newsletter (markdown +
JSON sections)."""
from __future__ import annotations

import json

from backend.models.schemas import Article, NewsletterDeal, NewsletterSection
from backend.pipeline.modal_client import chat_json
from backend.pipeline.prompts import NEWSLETTER_SYSTEM_PROMPT


def draft_newsletter(articles: list[Article]) -> tuple[str, list[NewsletterSection]]:
    if not articles:
        empty_md = "# FMCG Deal Intelligence\n\nNo qualifying deal activity found in this run."
        return empty_md, []

    payload = {
        "articles": [
            {
                "title": a.title,
                "companies": a.companies,
                "deal_type": a.deal_type,
                "deal_amount": a.deal_amount,
                "one_line_summary": a.one_line_summary,
                "credibility_tier": a.credibility_tier.value if a.credibility_tier else "C",
                "sources": [a.source_domain, *a.also_reported_by],
                "url": a.url,
            }
            for a in articles
        ]
    }
    result = chat_json(NEWSLETTER_SYSTEM_PROMPT, json.dumps(payload), max_tokens=6000)

    markdown = result.get("markdown", "")
    sections_raw = result.get("sections", [])
    sections = [NewsletterSection(**s) for s in sections_raw]

    return markdown, sections
