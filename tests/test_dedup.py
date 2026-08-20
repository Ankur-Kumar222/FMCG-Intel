from backend.models.schemas import Article, CredibilityTier
from backend.pipeline.dedup import dedupe_exact_urls, dedupe_near_duplicates, deduplicate


def make(title, url, domain, tier=None):
    a = Article(title=title, url=url, source_domain=domain)
    a.credibility_tier = tier
    return a


def test_exact_url_dedup_ignores_query_params():
    articles = [
        make("Story", "https://reuters.com/a?utm=1", "reuters.com"),
        make("Story", "https://reuters.com/a?utm=2", "reuters.com"),
    ]
    result = dedupe_exact_urls(articles)
    assert len(result) == 1


def test_near_duplicate_titles_are_merged():
    articles = [
        make(
            "Nestle acquires local snack brand for $50M",
            "https://reuters.com/a",
            "reuters.com",
            CredibilityTier.A,
        ),
        make(
            "Nestle acquires local snack brand for $50 million",
            "https://unknown.xyz/b",
            "unknown.xyz",
            CredibilityTier.C,
        ),
    ]
    result = dedupe_near_duplicates(articles)
    assert len(result) == 1
    assert result[0].source_domain == "reuters.com"
    assert "unknown.xyz" in result[0].also_reported_by


def test_distinct_stories_are_kept_separate():
    articles = [
        make("Nestle acquires snack brand", "https://a.com/1", "a.com"),
        make("Unilever raises stake in dairy startup", "https://b.com/2", "b.com"),
    ]
    result = deduplicate(articles)
    assert len(result) == 2
