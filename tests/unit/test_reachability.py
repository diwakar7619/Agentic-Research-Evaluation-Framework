import pytest

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
    SourceReachability,
)


class Backend:

    def __init__(
        self,
        name,
        supported=True,
        content="content",
        fail=False,
    ):
        self.name = name
        self.supported = supported
        self.content = content
        self.fail = fail

    def supports(self, source_url):
        return self.supported

    def read(self, source_url):
        if self.fail:
            raise RuntimeError(
                f"{self.name} failed"
            )

        return ReachabilityResult(
            source_url=source_url,
            content=self.content,
            backend=self.name,
            attempts=1,
        )


def test_first_successful_backend_wins():
    resolver = SourceReachability(
        (
            Backend("primary"),
            Backend("fallback"),
        )
    )

    result = resolver.resolve(
        "https://example.com"
    )

    assert result.backend == "primary"
    assert result.attempts == 1


def test_failed_backend_falls_back():
    resolver = SourceReachability(
        (
            Backend("primary", fail=True),
            Backend("fallback"),
        )
    )

    result = resolver.resolve(
        "https://example.com"
    )

    assert result.backend == "fallback"
    assert result.attempts == 2


def test_unsupported_backend_is_skipped():
    resolver = SourceReachability(
        (
            Backend("unsupported", supported=False),
            Backend("working"),
        )
    )

    result = resolver.resolve(
        "https://example.com"
    )

    assert result.backend == "working"
    assert result.attempts == 1


def test_all_supported_backends_failing_isolated():
    resolver = SourceReachability(
        (
            Backend("primary", fail=True),
            Backend("fallback", fail=True),
        )
    )

    with pytest.raises(
        RuntimeError,
        match="No reachable backend succeeded",
    ):
        resolver.resolve(
            "https://example.com"
        )


def test_no_backend_supporting_source():
    resolver = SourceReachability(
        (
            Backend("github", supported=False),
        )
    )

    with pytest.raises(
        RuntimeError,
        match="No backend supports source",
    ):
        resolver.resolve(
            "https://example.com"
        )


def test_doctor_reports_backend():
    resolver = SourceReachability(
        (
            Backend("web"),
            Backend("github"),
        )
    )

    health = resolver.doctor()

    assert len(health) == 2
    assert all(
        isinstance(item, BackendHealth)
        for item in health
    )
    assert {
        item.name
        for item in health
    } == {
        "web",
        "github",
    }

    assert all(
        not item.available
        for item in health
    )

    assert all(
        "No health probe implemented."
        in item.detail
        for item in health
    )
