"""Ingestion: fire a fixed set of Tavily searches tuned for FMCG deal activity."""
from __future__ import annotations

import os
from urllib.parse import urlparse

from tavily import TavilyClient

from backend.models.schemas import Article

SEARCH_QUERIES = [
    "FMCG acquisition news",
    "consumer goods company merger",
    "FMCG startup funding round",
    "FMCG private equity stake investment",
    "packaged food company acquires",
    "beverage company acquisition deal",
    "personal care company investment funding",
    "FMCG divestment sale business unit",
]

DEFAULT_RECENCY_DAYS = 7


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def run_ingestion(
    queries: list[str] | None = None,
    days: int = DEFAULT_RECENCY_DAYS,
    max_results_per_query: int = 8,
) -> list[Article]:
    """Query Tavily for each search term and normalize hits into Article records."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY is not set")

    client = TavilyClient(api_key=api_key)
    queries = queries or SEARCH_QUERIES
    articles: list[Article] = []

    for query in queries:
        response = client.search(
            query=query,
            search_depth="basic",
            topic="news",
            days=days,
            max_results=max_results_per_query,
        )
        for result in response.get("results", []):
            url = result.get("url", "")
            if not url:
                continue
            articles.append(
                Article(
                    title=result.get("title", "").strip(),
                    url=url,
                    snippet=(result.get("content") or "")[:1000],
                    published_date=result.get("published_date"),
                    source_domain=_domain(url),
                    raw_query=query,
                )
            )

    return articles
