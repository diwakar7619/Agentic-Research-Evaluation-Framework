from collector.github_bulk import (
    collect_relevant_files,
)
from collector.web import fetch_webpage
from discovery.github import (
    search_repositories,
)
from discovery.web import (
    WebSearchDiscoverer,
)
from research.github_adapter import (
    GitHubSourceAdapter,
)
from research.router import SourceRouter
from research.web_adapter import (
    WebSourceAdapter,
)


def build_real_router() -> SourceRouter:

    router = SourceRouter()

    web = WebSourceAdapter(
        discoverer=WebSearchDiscoverer(),
        fetcher=fetch_webpage,
    )

    github = GitHubSourceAdapter(
        discoverer=search_repositories,
        collector=collect_relevant_files,
    )

    router.register(
        "web",
        web.discover,
        web.collect,
    )

    router.register(
        "github",
        github.discover,
        github.collect,
    )

    return router
