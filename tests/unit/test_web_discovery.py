from discovery.web import WebSearchDiscoverer


def test_web_search_returns_normalized_results():

    discoverer = WebSearchDiscoverer()

    results = discoverer.search(
        "Python FastAPI",
        limit=3,
    )

    assert isinstance(
        results,
        list,
    )

    assert len(results) > 0

    for result in results:

        assert result["title"]
        assert result["url"]
        assert result["url"].startswith(
            ("http://", "https://")
        )
