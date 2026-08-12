from .source import (
    CollectedSource,
    SourceCandidate,
)


class InMemoryDiscoverer:

    def __init__(
        self,
        sources: list[SourceCandidate],
    ):
        self.sources = list(sources)

    def discover(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SourceCandidate]:

        if not query.strip():
            raise ValueError(
                "query is required."
            )

        return self.sources[:limit]


class InMemoryCollector:

    def __init__(
        self,
        documents: dict[str, str],
    ):
        self.documents = dict(documents)

    def collect(
        self,
        candidate: SourceCandidate,
    ) -> CollectedSource:

        if candidate.source_id not in self.documents:
            raise KeyError(
                candidate.source_id
            )

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=self.documents[
                candidate.source_id
            ],
            metadata=candidate.metadata,
        )
