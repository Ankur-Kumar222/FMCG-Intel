from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CredibilityTier(str, Enum):
    A = "A"  # major wire services / financial press
    B = "B"  # recognized trade press
    C = "C"  # unrecognized source


class Article(BaseModel):
    title: str
    url: str
    snippet: str = ""
    published_date: Optional[str] = None
    source_domain: str
    raw_query: str = ""

    # populated as the article moves through the pipeline
    also_reported_by: list[str] = Field(default_factory=list)
    credibility_tier: Optional[CredibilityTier] = None
    is_relevant: Optional[bool] = None
    relevance_score: Optional[float] = None
    deal_type: Optional[str] = None
    companies: list[str] = Field(default_factory=list)
    deal_amount: Optional[str] = None
    one_line_summary: Optional[str] = None


class NewsletterDeal(BaseModel):
    headline: str
    companies: list[str]
    deal_type: str
    deal_amount: Optional[str] = None
    summary: str
    sources: list[str]
    credibility_tier: CredibilityTier


class NewsletterSection(BaseModel):
    title: str
    deals: list[NewsletterDeal]


class NewsletterRun(BaseModel):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    query_set: list[str] = Field(default_factory=list)
    raw_articles: list[Article] = Field(default_factory=list)
    deduped_count: int = 0
    relevant_articles: list[Article] = Field(default_factory=list)
    newsletter_markdown: str = ""
    newsletter_sections: list[NewsletterSection] = Field(default_factory=list)
    status: str = "running"  # running | success | failed
    error: Optional[str] = None
