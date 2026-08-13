from __future__ import annotations

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class YouTubeAdapter:
    """YouTube transcript/content access boundary."""

    name = "youtube"

    def __init__(
        self,
        reader,
    ) -> None:
        self.reader = reader

    def supports(
        self,
        source_url: str,
    ) -> bool:
        value = source_url.lower()

        return (
            "youtube.com/" in value
            or "youtu.be/" in value
        )

    def read(
        self,
        source_url: str,
    ) -> ReachabilityResult:
        content = self.reader(source_url)

        if not isinstance(content, str):
            raise RuntimeError(
                "YouTube reader returned non-string content."
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
