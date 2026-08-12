from dataclasses import dataclass

from research.source import (
    CollectedSource,
    SourceCandidate,
)


@dataclass
class WebSourceAdapter:

    discoverer: object
    fetcher: object

    source_type: str = "web"

    def discover(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SourceCandidate]:

        results = self.discoverer.search(
            query,
            limit=limit,
        )

        return [
            SourceCandidate(
                source_id=f"web:{index}",
                source_type=self.source_type,
                title=item.get(
                    "title",
                    "",
                ),
                url=item["url"],
                metadata=item,
            )
            for index, item in enumerate(results)
            if item.get("url")
        ]

    def collect(
        self,
        candidate: SourceCandidate,
    ) -> CollectedSource:

        content = self.fetcher(
            candidate.url
        )

        if not content or not str(content).strip():
            raise ValueError(
                f"No content extracted from "
                f"{candidate.url}"
            )

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=str(content),
            metadata=candidate.metadata,
        )
