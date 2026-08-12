from research.router import SourceRouter
from research.source import (
    CollectedSource,
    SourceCandidate,
)


def test_router_supports_multiple_source_types():

    router = SourceRouter()

    router.register(
        "web",
        lambda query, limit=10: [
            SourceCandidate(
                source_id="web:1",
                source_type="web",
                title="Web result",
                url="https://example.com",
                metadata={},
            )
        ],
        lambda candidate: CollectedSource(
            source_id=candidate.source_id,
            source_type="web",
            title=candidate.title,
            url=candidate.url,
            content="web evidence",
            metadata={},
        ),
    )

    router.register(
        "github",
        lambda query, limit=10: [
            SourceCandidate(
                source_id="github:1",
                source_type="github",
                title="GitHub result",
                url="https://github.com/example/repo",
                metadata={},
            )
        ],
        lambda candidate: CollectedSource(
            source_id=candidate.source_id,
            source_type="github",
            title=candidate.title,
            url=candidate.url,
            content="github evidence",
            metadata={},
        ),
    )

    web = router.discover(
        "web",
        "AI",
        limit=1,
    )

    github = router.discover(
        "github",
        "AI",
        limit=1,
    )

    assert web[0].source_type == "web"
    assert github[0].source_type == "github"

    assert (
        router.collect(web[0]).content
        == "web evidence"
    )

    assert (
        router.collect(github[0]).content
        == "github evidence"
    )
