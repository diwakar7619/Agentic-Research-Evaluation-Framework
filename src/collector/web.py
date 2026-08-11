from typing import Optional

import httpx
import trafilatura


DEFAULT_TIMEOUT = 20.0


def fetch_webpage(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> Optional[str]:
    """Fetch a public webpage and extract its main text content."""

    response = httpx.get(
        url,
        headers={
            "User-Agent": "ai-engineer-research/0.1",
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=timeout,
        follow_redirects=True,
    )

    response.raise_for_status()

    return trafilatura.extract(
        response.text,
        include_links=True,
        include_tables=True,
    )
