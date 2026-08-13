from __future__ import annotations

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class GitHubAdapter:
    """GitHub access boundary."""

    name = "github"

    def __init__(
        self,
        reader,
    ) -> None:
        self.reader = reader

    def supports(
        self,
        source_url: str,
    ) -> bool:
        return "github.com/" in source_url.lower()

    def read(
        self,
        source_url: str,
    ) -> ReachabilityResult:
        content = self.reader(source_url)

        if not isinstance(content, str):
            raise RuntimeError(
                "GitHub reader returned non-string content."
            )

        return ReachabilityResult(
            source_url=source_url,
            content=content,
            backend=self.name,
            attempts=1,
        )

    def health(self) -> BackendHealth:
        return BackendHealth(
            name=self.name,
            available=True,
            detail="Reader configured.",
        )
