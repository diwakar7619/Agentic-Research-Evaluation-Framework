from dataclasses import dataclass

from research.result import (
    ResearchEvidence,
    ResearchResult,
)
from research.task import ResearchTask
from research.validator import ResearchValidator


@dataclass
class MultiSourceResearchRunner:

    router: object
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
                6,
            )
        )

        candidates = []

        for source_type in task.source_types:

            discovered = self.router.discover(
                source_type,
                task.question,
                limit=max_sources,
            )

            candidates.extend(
                discovered
            )

            if len(candidates) >= max_sources:
                break

        candidates = candidates[
            :max_sources
        ]

        if not candidates:
            raise ValueError(
                "No research sources discovered."
            )

        evidence = []
        collected = 0

        for candidate in candidates:

            try:

                source = self.router.collect(
                    candidate
                )

            except Exception:
                continue

            content = str(
                source.content
            ).strip()

            if not content:
                continue

            collected += 1

            evidence.append(
                ResearchEvidence(
                    source_id=source.source_id,
                    source_url=source.url,
                    text=content,
                    relevance=0.0,
                )
            )

        if not evidence:
            raise ValueError(
                "No research sources were collected."
            )

        answer = self.extractor.extract(
            question=task.question,
            evidence=tuple(evidence),
            schema=task.extraction_schema,
        )

        result = ResearchResult(
            question=task.question,
            answer=answer,
            evidence=tuple(evidence),
            sources_considered=len(candidates),
            sources_collected=collected,
        )

        return self.validator.validate(
            result
        )
