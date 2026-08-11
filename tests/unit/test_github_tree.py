from discovery.github_tree import discover_relevant_files


def test_discover_relevant_files(monkeypatch):
    import httpx

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "tree": [
                    {
                        "path": "README.md",
                        "type": "blob",
                    },
                    {
                        "path": "phases/11-llm-engineering/06-rag/docs/en.md",
                        "type": "blob",
                    },
                    {
                        "path": "phases/14-agent-engineering/01-agent/docs/en.md",
                        "type": "blob",
                    },
                    {
                        "path": "phases/14-agent-engineering/01-agent/quiz.json",
                        "type": "blob",
                    },
                    {
                        "path": "phases/01-math-foundations/docs/en.md",
                        "type": "blob",
                    },
                ]
            }

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_get)

    result = discover_relevant_files()

    assert "README.md" in result
    assert "phases/11-llm-engineering/06-rag/docs/en.md" in result
    assert "phases/14-agent-engineering/01-agent/docs/en.md" in result

    assert not any("/quiz.json" in path for path in result)
    assert not any("math-foundations" in path for path in result)
