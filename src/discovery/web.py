from ddgs import DDGS


class WebSearchDiscoverer:
    """
    No-key web search provider.

    Returns normalized search-result dictionaries.
    The research layer remains independent of the search provider.
    """

    def __init__(
        self,
        *,
        region: str = "wt-wt",
        safesearch: str = "moderate",
    ):
        self.region = region
        self.safesearch = safesearch

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[dict]:

        if not query.strip():
            raise ValueError(
                "query is required."
            )

        results = DDGS().text(
            query,
            region=self.region,
            safesearch=self.safesearch,
            max_results=limit,
        )

        return [
            {
                "title": item.get(
                    "title",
                    "",
                ),
                "url": item.get(
                    "href",
                    "",
                ),
                "snippet": item.get(
                    "body",
                    "",
                ),
            }
            for item in results
            if item.get("href")
        ]
