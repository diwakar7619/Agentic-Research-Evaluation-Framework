from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
from dataclasses import dataclass

from .alignment import alignment_score
from .result import (
    ResearchEvidence,
    ResearchResult,
)
from .source import (
    SourceCollector,
    SourceDiscoverer,
)
from .task import ResearchTask
from .telemetry import ResearchTelemetry
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

        run_id = str(
            task.metadata.get(
                "run_id",
                "research-run",
            )
        )

        telemetry = ResearchTelemetry(
            run_id=run_id,
        )

        telemetry.increment(
            "evidence_alignment_rejected",
            0,
        )

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

        telemetry.increment(
            "sources_discovered",
            len(candidates),
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

        telemetry.increment(
            "sources_collected",
            len(collected),
        )

        relevant_evidence = []

        for source in collected:
            content = source.content.strip()

            if not content:
                continue

            relevance = alignment_score(
                task.question,
                content,
            )

            # Preserve recall when only one source was collected.
            # When multiple sources are available, reject sources
            # with zero lexical alignment before extraction.
            if (
                len(collected) > 1
                and relevance <= 0.0
            ):
                telemetry.increment(
                    "evidence_alignment_rejected",
                )
                continue

            relevant_evidence.append(
                ResearchEvidence(
                    source_id=source.source_id,
                    source_url=source.url,
                    text=content,
                    relevance=relevance,
                )
            )

        evidence = tuple(relevant_evidence)

        with telemetry.stage("extraction"):
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

        validated = self.validator.validate(
            result
        )

        telemetry_dir = task.metadata.get(
            "telemetry_dir"
        )

        if telemetry_dir:
            output_dir = Path(str(telemetry_dir))
            output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path = (
                output_dir
                / f"{run_id}.json"
            )

            output_path.write_text(
                json.dumps(
                    telemetry.summary(),
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

        return validated
