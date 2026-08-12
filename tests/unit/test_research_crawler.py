from pathlib import Path

import pytest

from research.crawler import (
    CrawlPolicy,
    ResearchCrawler,
    canonicalize_url,
    content_hash,
    normalize_text,
)


def test_policy_has_bounded_defaults():

    policy = CrawlPolicy()

    assert policy.max_requests > 0
    assert policy.max_depth >= 0
    assert policy.max_concurrency > 0
    assert policy.max_requests_per_minute > 0
    assert policy.max_request_retries >= 0
    assert policy.request_timeout_seconds > 0
    assert policy.respect_robots_txt is True


def test_normalize_text():

    assert (
        normalize_text(
            "  hello \n world   again "
        )
        == "hello world again"
    )


def test_content_hash_is_deterministic():

    first = content_hash("hello")
    second = content_hash("hello")

    assert first == second
    assert len(first) == 64


def test_normalize_text_accepts_beautifulsoup_tag():

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        "<title>  Hello   World </title>",
        "lxml",
    )

    assert (
        normalize_text(soup.title)
        == "Hello World"
    )


def test_normalize_text_accepts_beautifulsoup_document():

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        "<html><body><p>Hello</p><p>World</p></body></html>",
        "lxml",
    )

    assert (
        normalize_text(soup)
        == "Hello World"
    )


def test_canonicalize_url_removes_tracking():

    result = canonicalize_url(
        "HTTPS://Example.COM/docs/"
        "?b=2&a=1&utm_source=test"
    )

    assert (
        result
        == "https://example.com/docs?a=1&b=2"
    )


def test_canonicalize_url_removes_fragment():

    result = canonicalize_url(
        "https://example.com/page#section"
    )

    assert result == (
        "https://example.com/page"
    )


def test_canonicalize_url_removes_utm_family():

    result = canonicalize_url(
        "https://example.com/page"
        "?utm_source=x"
        "&utm_medium=y"
        "&utm_campaign=z"
        "&id=42"
    )

    assert result == (
        "https://example.com/page?id=42"
    )


def test_canonicalize_url_preserves_non_tracking_parameters():

    result = canonicalize_url(
        "https://example.com/page"
        "?q=research"
        "&page=2"
        "&utm_source=test"
    )

    assert result == (
        "https://example.com/page"
        "?page=2&q=research"
    )


def test_domain_policy():

    from research.crawler import _allowed_url

    assert _allowed_url(
        "https://example.com/page",
        ("example.com",),
    )

    assert _allowed_url(
        "https://docs.example.com/page",
        ("example.com",),
    )

    assert not _allowed_url(
        "https://other.com/page",
        ("example.com",),
    )


def test_empty_urls_are_rejected(
    tmp_path: Path,
):

    crawler = ResearchCrawler(
        lake_dir=tmp_path,
    )

    with pytest.raises(ValueError):
        import asyncio

        asyncio.run(
            crawler.crawl([])
        )


def test_crawler_accepts_policy(
    tmp_path: Path,
):

    policy = CrawlPolicy(
        max_requests=5,
        max_depth=2,
        max_concurrency=2,
    )

    crawler = ResearchCrawler(
        policy=policy,
        lake_dir=tmp_path,
    )

    assert crawler.policy == policy
    assert crawler.lake_dir == tmp_path


def test_policy_supports_adaptive_selector():

    policy = CrawlPolicy(
        required_selector="#app",
        selector_timeout_seconds=7.0,
    )

    assert policy.required_selector == "#app"
    assert policy.selector_timeout_seconds == 7.0
