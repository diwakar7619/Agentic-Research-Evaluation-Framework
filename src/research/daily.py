from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
import trafilatura
from ddgs import DDGS

from .source import (
    CollectedSource,
    SourceCandidate,
)


@dataclass
class DDGSWebDiscoverer:
    """Production web discovery adapter."""

    max_results: int = 5
    region: str = "us-en"

    def discover(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SourceCandidate]:

        if not query.strip():
            raise ValueError("query is required.")

        requested = min(
            max(limit, 1),
            self.max_results,
        )

        results = DDGS().text(
            query,
            region=self.region,
            safesearch="moderate",
            max_results=requested,
        )

        candidates: list[SourceCandidate] = []

        for index, item in enumerate(results):

            url = str(
                item.get("href", "")
            ).strip()

            if not url:
                continue

            title = str(
                item.get("title", "")
            ).strip()

            candidates.append(
                SourceCandidate(
                    source_id=f"web-{index + 1}",
                    source_type="web",
                    title=title or url,
                    url=url,
                    metadata={
                        "search_query": query,
                        "snippet": str(
                            item.get("body", "")
                        ),
                    },
                )
            )

        return candidates


@dataclass
class HttpWebCollector:
    """Bounded web-content collector."""

    timeout_seconds: float = 20.0
    max_content_chars: int = 30000

    def collect(
        self,
        candidate: SourceCandidate,
    ) -> CollectedSource:

        parsed = urlparse(candidate.url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                f"Unsupported URL scheme: {candidate.url}"
            )

        response = httpx.get(
            candidate.url,
            timeout=self.timeout_seconds,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "ai-engineer-research/0.1 "
                    "(research client)"
                )
            },
        )

        response.raise_for_status()

        text = trafilatura.extract(
            response.text,
            include_links=True,
            include_tables=True,
        )

        if not text:
            raise ValueError(
                f"Could not extract readable content: "
                f"{candidate.url}"
            )

        text = text[: self.max_content_chars]

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=str(response.url),
            content=text,
            metadata={
                **candidate.metadata,
                "status_code": response.status_code,
            },
        )
