"""De-duplication: exact URL matching + fuzzy near-duplicate title matching.

Deliberately rule-based (no embeddings) so the logic stays fast, cheap, and
easy to explain in the README:

1. Exact pass: normalize each URL (strip query params/fragments, lowercase
   host) and drop repeats.
2. Near-dup pass: within the surviving set, compare titles pairwise with
   RapidFuzz's token_sort_ratio. Two titles scoring above NEAR_DUP_THRESHOLD
   are treated as the same underlying story. We keep the copy from the
   higher-credibility source (tier already assigned by credibility.py must
   run before this, or we fall back to "keep first seen") and record the
   other outlet(s) in `also_reported_by` so the newsletter can cite multiple
   sources for one deal instead of silently dropping coverage.
"""
from __future__ import annotations

from urllib.parse import urlparse, urlunparse

from rapidfuzz import fuzz

from backend.models.schemas import Article, CredibilityTier

NEAR_DUP_THRESHOLD = 85

_TIER_RANK = {CredibilityTier.A: 0, CredibilityTier.B: 1, CredibilityTier.C: 2, None: 3}


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))


def dedupe_exact_urls(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    result = []
    for article in articles:
        key = _normalize_url(article.url)
        if key in seen:
            continue
        seen.add(key)
        result.append(article)
    return result


def dedupe_near_duplicates(articles: list[Article]) -> list[Article]:
    kept: list[Article] = []

    for candidate in articles:
        match_idx = None
        for idx, existing in enumerate(kept):
            score = fuzz.token_sort_ratio(candidate.title, existing.title)
            if score >= NEAR_DUP_THRESHOLD:
                match_idx = idx
                break

        if match_idx is None:
            kept.append(candidate)
            continue

        existing = kept[match_idx]
        if _TIER_RANK[candidate.credibility_tier] < _TIER_RANK[existing.credibility_tier]:
            # candidate is from a more credible source -> it becomes the kept record
            candidate.also_reported_by = existing.also_reported_by + [existing.source_domain]
            kept[match_idx] = candidate
        else:
            existing.also_reported_by = existing.also_reported_by + [candidate.source_domain]

    return kept


def deduplicate(articles: list[Article]) -> list[Article]:
    """Run both dedup passes. Credibility tiers should already be set for
    best results (so we keep the most credible copy of a duplicated story),
    but the function degrades gracefully to "keep first seen" otherwise."""
    return dedupe_near_duplicates(dedupe_exact_urls(articles))
