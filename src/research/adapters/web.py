from __future__ import annotations

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class WebAdapter:
    """
    Web adapter boundary.

    Network implementation remains intentionally injected so the
    research system does not hard-code a specific web reader.
    """

    name = "web"

    def __init__(
        self,
        reader,
    ) -> None:
        self.reader = reader

    def supports(
        self,
        source_url: str,
    ) -> bool:
        return source_url.startswith(
            ("http://", "https://")
        )

    def read(
        self,
        source_url: str,
    ) -> ReachabilityResult:
        content = self.reader(source_url)

        if not isinstance(content, str):
            raise RuntimeError(
                "Web reader returned non-string content."
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
