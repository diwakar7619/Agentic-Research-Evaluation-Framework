import httpx

from collector.web import fetch_webpage


def test_fetch_webpage_extracts_text(monkeypatch):
    class MockResponse:
        text = """
        <html>
            <body>
                <nav>Navigation</nav>
                <main>
                    <h1>AI Engineering</h1>
                    <p>Production AI systems require reliable engineering.</p>
                </main>
                <footer>Footer</footer>
            </body>
        </html>
        """

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    result = fetch_webpage("https://example.com")

    assert result is not None
    assert "AI Engineering" in result
    assert "Production AI systems" in result
