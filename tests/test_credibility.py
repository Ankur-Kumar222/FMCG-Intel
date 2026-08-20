from backend.models.schemas import Article, CredibilityTier
from backend.pipeline.credibility import classify_domain, tag_credibility


def test_classify_tier_a():
    assert classify_domain("reuters.com") == CredibilityTier.A


def test_classify_tier_b():
    assert classify_domain("fooddive.com") == CredibilityTier.B


def test_classify_unknown_is_tier_c():
    assert classify_domain("some-random-blog.xyz") == CredibilityTier.C


def test_tag_credibility_sets_field_on_all_articles():
    articles = [
        Article(title="a", url="https://reuters.com/x", source_domain="reuters.com"),
        Article(title="b", url="https://unknown.xyz/y", source_domain="unknown.xyz"),
    ]
    tag_credibility(articles)
    assert articles[0].credibility_tier == CredibilityTier.A
    assert articles[1].credibility_tier == CredibilityTier.C
