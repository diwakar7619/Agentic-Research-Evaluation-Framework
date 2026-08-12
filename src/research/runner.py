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

        collected = []

        for candidate in allowed:

            collected.append(
                self.collector.collect(
                    candidate
                )
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
