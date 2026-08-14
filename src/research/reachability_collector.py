from __future__ import annotations

from research.reachability import SourceReachability
from research.source import (
    CollectedSource,
    SourceCandidate,
)


class ReachabilitySourceCollector:
    """
    Concrete SourceCollector implementation.

    The research engine only sees the stable
    SourceCandidate -> CollectedSource contract.

    All external access decisions are delegated to
    SourceReachability.
    """

    def __init__(
        self,
        reachability: SourceReachability,
    ) -> None:
        self.reachability = reachability

    def collect(
        self,
        candidate: SourceCandidate,
    ) -> CollectedSource:

        if not candidate.url.strip():
            raise ValueError(
                "Source candidate URL must not be empty."
            )

        result = self.reachability.resolve(
            candidate.url
        )

        result.validate()

        content = result.content.strip()

        if not content:
            raise ValueError(
                "Collected source content must not be empty."
            )

        metadata = dict(candidate.metadata)

        from datetime import datetime, timezone

        metadata.update(
            {
                "collection_backend": result.backend,
                "collection_attempts": result.attempts,
                "retrieved_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            }
        )

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=content,
            metadata=metadata,
        )
