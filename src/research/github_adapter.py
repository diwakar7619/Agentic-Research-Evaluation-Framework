from dataclasses import dataclass
from urllib.parse import urlparse

from research.source import (
    CollectedSource,
    SourceCandidate,
)


@dataclass
class GitHubSourceAdapter:

    discoverer: object
    collector: object

    source_type: str = "github"

    def discover(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SourceCandidate]:

        candidates = self.discoverer(
            query,
            per_page=limit,
        )

        return [
            SourceCandidate(
                source_id=(
                    f"github:"
                    f"{item.username}/"
                    f"{item.repository_name}"
                ),
                source_type=self.source_type,
                title=item.repository_name,
                url=item.repository_url,
                metadata={
                    "username": item.username,
                    "repository": item.repository_name,
                    "profile_url": item.profile_url,
                },
            )
            for item in candidates
        ]

    def collect(
        self,
        candidate: SourceCandidate,
    ) -> CollectedSource:

        parsed = urlparse(candidate.url)

        parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if len(parts) < 2:
            raise ValueError(
                f"Invalid GitHub repository URL: "
                f"{candidate.url}"
            )

        owner = parts[0]
        repository = parts[1]

        # Existing collector contract is intentionally
        # used instead of introducing a second GitHub client.
        collected = self.collector(
            owner,
            repository,
        )

        if not collected:
            raise ValueError(
                f"No GitHub content collected from "
                f"{candidate.url}"
            )

        if isinstance(collected, str):

            content = collected

        else:

            content = str(collected)

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=content,
            metadata=candidate.metadata,
        )
