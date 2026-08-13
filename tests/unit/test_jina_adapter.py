import httpx

from research.adapters.jina import JinaWebAdapter


def test_jina_constructor_rejects_invalid_attempts():
    try:
        JinaWebAdapter(max_attempts=0)
    except ValueError as exc:
        assert str(exc) == (
            "max_attempts must be >= 1."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_jina_constructor_rejects_invalid_timeout():
    try:
        JinaWebAdapter(timeout_seconds=0)
    except ValueError as exc:
        assert str(exc) == (
            "timeout_seconds must be > 0."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_jina_supports_http_urls():
    adapter = JinaWebAdapter()

    assert adapter.supports(
        "https://example.com"
    )

    assert adapter.supports(
        "http://example.com"
    )


def test_jina_supports_only_http_urls():
    adapter = JinaWebAdapter()

    assert not adapter.supports(
        "ftp://example.com"
    )
