from research.memory import (
    InMemoryCollector,
)
from research.multi_source_runner import (
    MultiSourceResearchRunner,
)
from research.result import ResearchResult
from research.source import (
    CollectedSource,
    SourceCandidate,
)
from research.task import ResearchTask
from research.validator import ResearchValidator


class Router:

    def __init__(self):

        self.candidates = [
            SourceCandidate(
                source_id="web:1",
                source_type="web",
                title="Web source",
                url="https://example.com",
                metadata={},
            ),
            SourceCandidate(
                source_id="github:1",
                source_type="github",
                title="GitHub source",
                url="https://github.com/example/repo",
                metadata={},
            ),
        ]

    def discover(
        self,
        source_type,
        query,
        *,
        limit=10,
    ):

        return [
            item
            for item in self.candidates
            if item.source_type == source_type
        ][:limit]

    def collect(
        self,
        candidate,
    ):

        return CollectedSource(
            source_id=candidate.source_id,
            source_type=candidate.source_type,
            title=candidate.title,
            url=candidate.url,
            content=(
                f"Evidence from "
                f"{candidate.source_type}"
            ),
            metadata={},
        )


class Extractor:

    def extract(
        self,
        *,
        question,
        evidence,
        schema,
    ):

        return {
            "status": "extracted",
            "evidence_length": len(
                evidence
            ),
            "question": question,
        }


def test_multi_source_runner():

    task = ResearchTask(
        name="multi_source",
        question="Research AI systems.",
        source_types=(
            "web",
            "github",
        ),
        extraction_schema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string"
                }
            },
        },
        metadata={
            "max_sources": 2,
        },
    )

    runner = MultiSourceResearchRunner(
        router=Router(),
        extractor=Extractor(),
        validator=ResearchValidator(),
    )

    result = runner.run(task)

    assert isinstance(
        result,
        ResearchResult,
    )

    assert result.sources_considered == 2
    assert result.sources_collected == 2
    assert len(result.evidence) == 2
    assert result.answer["status"] == "extracted"
