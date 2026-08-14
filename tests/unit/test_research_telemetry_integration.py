import json
from pathlib import Path

from research.result import ResearchResult
from research.runner import ResearchRunner
from research.source import (
    CollectedSource,
    SourceCandidate,
)
from research.task import ResearchTask


class Discoverer:

    def discover(
        self,
        query,
        *,
        limit=10,
    ):

        return [
            SourceCandidate(
                source_id="integration-source",
                source_type="web",
                title="Relevant source",
                url="https://example.com/research",
                metadata={},
            )
        ]


class Collector:

    def collect(self, candidate):

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=(
                "Production AI agent research "
                "uses evidence and retrieval."
            ),
            metadata={},
        )


class Extractor:

    def __init__(self):
        self.received_evidence = None

    def extract(
        self,
        *,
        question,
        evidence,
        schema,
    ):

        self.received_evidence = tuple(
            evidence
        )

        return {
            "status": "ok",
            "evidence_count": len(evidence),
        }


class Validator:

    def validate(self, result):
        return result


def test_real_runner_telemetry_integration(
    tmp_path,
):

    extractor = Extractor()

    runner = ResearchRunner(
        discoverer=Discoverer(),
        collector=Collector(),
        extractor=extractor,
        validator=Validator(),
    )

    task = ResearchTask(
        name="telemetry-integration",
        question=(
            "Research production AI agent "
            "retrieval and evidence."
        ),
        source_types=("web",),
        extraction_schema={
            "status": "string",
        },
        metadata={
            "max_sources": 1,
            "run_id": "telemetry-integration-run",
            "telemetry_dir": str(tmp_path),
        },
    )

    result = runner.run(task)

    assert isinstance(
        result,
        ResearchResult,
    )

    assert (
        len(extractor.received_evidence)
        == 1
    )

    telemetry_file = (
        tmp_path
        / "telemetry-integration-run.json"
    )

    assert telemetry_file.exists()

    payload = json.loads(
        telemetry_file.read_text(
            encoding="utf-8"
        )
    )

    assert "stages" in payload
    assert "counters" in payload

    assert (
        payload["counters"]
        ["sources_discovered"]
        == 1
    )

    assert (
        payload["counters"]
        ["sources_collected"]
        == 1
    )

    assert (
        payload["counters"]
        ["evidence_alignment_rejected"]
        == 0
    )

    assert any(
        stage["name"] == "extraction"
        for stage in payload["stages"]
    )
