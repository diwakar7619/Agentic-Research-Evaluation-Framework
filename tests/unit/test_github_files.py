import httpx

from collector.github_files import fetch_github_file


def test_fetch_github_file(monkeypatch):
    class MockResponse:
        text = "# Example Project\nRAG application with embeddings."

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    result = fetch_github_file(
        "phases/11-llm-engineering/06-rag/docs/en.md"
    )

    assert "RAG application" in result
