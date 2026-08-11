import httpx
import pytest

from discovery.github import Candidate, search_repositories


def test_search_repositories_returns_candidates(monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "items": [
                    {
                        "name": "ai-project",
                        "html_url": "https://github.com/example-builder/ai-project",
                        "owner": {
                            "login": "example-builder",
                        },
                    }
                ]
            }

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    result = search_repositories("AI engineering")

    assert len(result) == 1
    assert result[0].username == "example-builder"
    assert result[0].profile_url == "https://github.com/example-builder"
    assert result[0].repository_name == "ai-project"
    assert result[0].repository_url == "https://github.com/example-builder/ai-project"
