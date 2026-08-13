from research.reachability import (
    ReachabilityResult,
    SourceReachability,
)
from research.reachability_collector import (
    ReachabilitySourceCollector,
)
from research.source import SourceCandidate


class WorkingBackend:

    name = "test-backend"

    def supports(self, source_url):
        return True

    def read(self, source_url):
        return ReachabilityResult(
            source_url=source_url,
            content="  collected research content  ",
            backend=self.name,
            attempts=1,
        )


class FailingBackend:

    name = "failing-backend"

    def supports(self, source_url):
        return True

    def read(self, source_url):
        raise RuntimeError(
            "intentional failure"
        )


def candidate():
    return SourceCandidate(
        source_id="source-1",
        source_type="web",
        title="Test Source",
        url="https://example.com",
        metadata={
            "original": "metadata",
        },
    )


def test_collector_returns_existing_contract():
    collector = ReachabilitySourceCollector(
        SourceReachability(
            (
                WorkingBackend(),
            )
        )
    )

    result = collector.collect(
        candidate()
    )

    assert result.source_id == "source-1"
    assert result.source_type == "web"
    assert result.title == "Test Source"
    assert result.url == "https://example.com"

    assert result.content == (
        "collected research content"
    )

    assert result.metadata["original"] == (
        "metadata"
    )

    assert result.metadata[
        "collection_backend"
    ] == "test-backend"

    assert result.metadata[
        "collection_attempts"
    ] == 1


def test_collector_preserves_fallback_attempt_count():
    collector = ReachabilitySourceCollector(
        SourceReachability(
            (
                FailingBackend(),
                WorkingBackend(),
            )
        )
    )

    result = collector.collect(
        candidate()
    )

    assert result.metadata[
        "collection_backend"
    ] == "test-backend"

    assert result.metadata[
        "collection_attempts"
    ] == 2


def test_empty_url_is_rejected():
    collector = ReachabilitySourceCollector(
        SourceReachability(
            (
                WorkingBackend(),
            )
        )
    )

    invalid = SourceCandidate(
        source_id="source-1",
        source_type="web",
        title="Invalid",
        url="",
        metadata={},
    )

    try:
        collector.collect(invalid)
    except ValueError as exc:
        assert str(exc) == (
            "Source candidate URL must not be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )
