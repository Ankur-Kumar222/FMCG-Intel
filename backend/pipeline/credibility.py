"""Credibility check: static, transparent domain-tier lookup.

No ML here on purpose -- a fixed allowlist is easy for a business user to
audit and easy to extend. Anything not on the list is Tier C ("unverified
source") and is still shown in the newsletter, just flagged, rather than
silently dropped -- credibility informs trust, it doesn't gate inclusion.
"""
from __future__ import annotations

from backend.models.schemas import Article, CredibilityTier

TIER_A_DOMAINS = {
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "apnews.com",
    "cnbc.com",
    "economictimes.indiatimes.com",
    "livemint.com",
    "business-standard.com",
    "moneycontrol.com",
}

TIER_B_DOMAINS = {
    "fooddive.com",
    "etretail.com",
    "just-food.com",
    "foodbev.com",
    "retaildive.com",
    "campaignindia.in",
    "beveragedaily.com",
    "cosmeticsbusiness.com",
    "foodnavigator.com",
    "just-drinks.com",
    "consumergoods.com",
    "prnewswire.com",
    "businesswire.com",
    "insidefmcg.com.au",
}


def classify_domain(domain: str) -> CredibilityTier:
    domain = domain.lower()
    if domain in TIER_A_DOMAINS:
        return CredibilityTier.A
    if domain in TIER_B_DOMAINS:
        return CredibilityTier.B
    return CredibilityTier.C


def tag_credibility(articles: list[Article]) -> list[Article]:
    for article in articles:
        article.credibility_tier = classify_domain(article.source_domain)
    return articles
