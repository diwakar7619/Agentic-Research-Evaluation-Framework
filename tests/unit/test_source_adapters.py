from research.adapters.github import GitHubAdapter
from research.adapters.web import WebAdapter
from research.adapters.youtube import YouTubeAdapter


def reader(url):
    return f"content:{url}"


def test_web_adapter():
    adapter = WebAdapter(reader)

    assert adapter.supports(
        "https://example.com"
    )

    result = adapter.read(
        "https://example.com"
    )

    assert result.backend == "web"
    assert result.content == (
        "content:https://example.com"
    )


def test_github_adapter():
    adapter = GitHubAdapter(reader)

    assert adapter.supports(
        "https://github.com/example/repo"
    )

    result = adapter.read(
        "https://github.com/example/repo"
    )

    assert result.backend == "github"


def test_youtube_adapter():
    adapter = YouTubeAdapter(reader)

    assert adapter.supports(
        "https://youtube.com/watch?v=test"
    )

    assert adapter.supports(
        "https://youtu.be/test"
    )

    result = adapter.read(
        "https://youtu.be/test"
    )

    assert result.backend == "youtube"
