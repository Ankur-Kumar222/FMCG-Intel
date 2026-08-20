"""Relevance scoring: cheap keyword prefilter, then a single batched LLM call.

Two stages, in order of cost:
1. Keyword prefilter (`is_plausible_deal_article`) -- an article must mention
   both an FMCG/category term AND a deal term to survive. This throws out
   the obviously-irrelevant majority (general company news, product launches,
   unrelated business news) for free, before we spend an LLM call on it.
2. The survivors are sent to the Modal LLM endpoint in ONE batched request,
   which confirms relevance and extracts structured deal fields (companies,
   deal type, amount, one-line summary) in the same pass -- so this step
   doubles as the content-extraction step the newsletter drafter consumes.
"""
from __future__ import annotations

from backend.models.schemas import Article
from backend.pipeline.modal_client import infer

FMCG_TERMS = [
    "fmcg", "consumer goods", "packaged food", "beverage", "snack", "dairy",
    "personal care", "household products", "cosmetics", "beauty brand",
    "grocery", "retail brand", "food company", "drinks company",
]

DEAL_TERMS = [
    "acqui", "merger", "merges", "stake", "invest", "funding", "raises",
    "ipo", "divest", "joint venture", " jv ", "buyout", "takeover",
    "acquisition", "acquires", "acquired",
]


def is_plausible_deal_article(article: Article) -> bool:
    text = f"{article.title} {article.snippet}".lower()
    has_fmcg_term = any(term in text for term in FMCG_TERMS)
    has_deal_term = any(term in text for term in DEAL_TERMS)
    return has_fmcg_term and has_deal_term


def prefilter(articles: list[Article]) -> list[Article]:
    return [a for a in articles if is_plausible_deal_article(a)]


def score_relevance(articles: list[Article]) -> list[Article]:
    """Send prefiltered articles to the Modal LLM in one batched call for
    final relevance confirmation + structured deal-field extraction."""
    candidates = prefilter(articles)
    if not candidates:
        return []

    payload = {
        "articles": [
            {"index": i, "title": a.title, "snippet": a.snippet, "source_domain": a.source_domain}
            for i, a in enumerate(candidates)
        ]
    }
    result = infer("score_relevance", payload)

    relevant: list[Article] = []
    for item in result.get("results", []):
        idx = item.get("index")
        if idx is None or idx >= len(candidates):
            continue
        article = candidates[idx]
        article.is_relevant = bool(item.get("is_relevant", False))
        article.relevance_score = float(item.get("relevance_score", 0.0))
        article.deal_type = item.get("deal_type")
        article.companies = item.get("companies", [])
        article.deal_amount = item.get("deal_amount")
        article.one_line_summary = item.get("one_line_summary")
        if article.is_relevant:
            relevant.append(article)

    return relevant
