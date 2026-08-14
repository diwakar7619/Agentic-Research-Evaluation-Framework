from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .result import (
    ResearchEvidence,
    ResearchResult,
)
from .source import (
    SourceCollector,
    SourceDiscoverer,
)
from .task import ResearchTask
from .validator import ResearchValidator


@dataclass
class ResearchRunner:

    discoverer: SourceDiscoverer
    collector: SourceCollector
    extractor: object
    validator: ResearchValidator

    def run(
        self,
        task: ResearchTask,
    ) -> ResearchResult:

        task.validate()

        max_sources = int(
            task.metadata.get(
                "max_sources",
                10,
            )
        )

        candidates = self.discoverer.discover(
            task.question,
            limit=max_sources,
        )

        allowed = [
            candidate
            for candidate in candidates
            if task.supports_source(
                candidate.source_type
            )
        ]

        max_collection_concurrency = int(
            task.metadata.get(
                "max_collection_concurrency",
                8,
            )
        )

        if max_collection_concurrency < 1:
            raise ValueError(
                "max_collection_concurrency must be at least 1."
            )

        def collect_one(candidate):
            try:
                return self.collector.collect(
                    candidate
                )
            except Exception:
                # A single inaccessible source must not
                # invalidate otherwise usable research.
                return None

        collected = []

        if allowed:
            with ThreadPoolExecutor(
                max_workers=min(
                    max_collection_concurrency,
                    len(allowed),
                ),
                thread_name_prefix="research-source",
            ) as executor:

                futures = [
                    executor.submit(
                        collect_one,
                        candidate,
                    )
                    for candidate in allowed
                ]

                # Preserve discovery order even though
                # collection executes concurrently.
                for future in futures:
                    source = future.result()

                    if source is not None:
                        collected.append(source)

        if not collected:
            raise ValueError(
                "No sources were collected."
            )

        evidence = tuple(
            ResearchEvidence(
                source_id=source.source_id,
                source_url=source.url,
                text=source.content,
            )
            for source in collected
            if source.content.strip()
        )

        answer = self.extractor.extract(
            question=task.question,
            evidence=evidence,
            schema=task.extraction_schema,
        )

        result = ResearchResult(
            question=task.question,
            answer=answer,
            evidence=evidence,
            sources_considered=len(
                candidates
            ),
            sources_collected=len(
                collected
            ),
        )

        return self.validator.validate(
            result
        )
