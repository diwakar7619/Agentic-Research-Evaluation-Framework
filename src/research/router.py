class SourceRouter:

    def __init__(self):
        self._sources = {}

    def register(
        self,
        source_type: str,
        discoverer,
        collector,
    ):
        if not source_type.strip():
            raise ValueError(
                "source_type cannot be empty."
            )

        self._sources[source_type] = (
            discoverer,
            collector,
        )

    def discover(
        self,
        source_type: str,
        query: str,
        *,
        limit: int = 10,
    ):
        if source_type not in self._sources:
            raise ValueError(
                f"Unknown source type: {source_type}"
            )

        discoverer, _ = self._sources[
            source_type
        ]

        return discoverer(
            query,
            limit=limit,
        )

    def collect(
        self,
        candidate,
    ):
        source_type = candidate.source_type

        if source_type not in self._sources:
            raise ValueError(
                f"Unknown source type: {source_type}"
            )

        _, collector = self._sources[
            source_type
        ]

        return collector(candidate)
