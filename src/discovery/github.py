from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class Candidate:
    username: str
    profile_url: str
    repository_name: str
    repository_url: str


GITHUB_API = "https://api.github.com"


def search_repositories(
    query: str,
    *,
    per_page: int = 10,
) -> list[Candidate]:
    """Discover GitHub repository candidates using public GitHub API."""

    response = httpx.get(
        f"{GITHUB_API}/search/repositories",
        params={
            "q": query,
            "per_page": per_page,
        },
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "ai-engineer-research",
        },
        timeout=20.0,
    )

    response.raise_for_status()

    items = response.json()["items"]

    return [
        Candidate(
            username=item["owner"]["login"],
            profile_url=f"https://github.com/{item['owner']['login']}",
            repository_name=item["name"],
            repository_url=item["html_url"],
        )
        for item in items
    ]
