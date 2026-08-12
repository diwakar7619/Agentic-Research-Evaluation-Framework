from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from research.executor import ResearchExecutor
from research.ollama import OllamaProvider
from research.planner import ResearchPlanner
from research.researcher import ResearchReport, Researcher
from research.runner import ResearchRunner
from research.store import ResearchStore
from research.synthesizer import ResearchSynthesizer
from research.task import ResearchTask
from research.validator import ResearchValidator


class FakeDiscoverer:
    def discover(self, question, limit=10):
        return [
            SimpleNamespace(
                source_id="integration-source",
                source_type="web",
                url="https://example.com",
            )
        ]


class FakeCollector:
    def collect(self, candidate):
        return SimpleNamespace(
            source_id=candidate.source_id,
            url=candidate.url,
            content=(
                "Python is a programming language "
                "used for general-purpose software development."
            ),
        )


class FakeExtractor:
    def extract(
        self,
        *,
        question,
        evidence,
        schema,
    ):
        return {
            "summary": (
                "The supplied evidence describes "
                "Python as a programming language."
            )
        }


def test_unified_researcher_real_runner_e2e():
    """
    Complete deterministic Phase 17 integration:

        ResearchTask
          -> ResearchPlanner
          -> ResearchExecutor
          -> REAL ResearchRunner
          -> discovery/collection/extraction/validation
          -> ResearchResult
          -> REAL Qwen synthesis
          -> REAL SQLite persistence
          -> ResearchReport

    Lower-level source dependencies are deterministic test doubles.
    The ResearchRunner itself is the production implementation.
    """

    with TemporaryDirectory() as directory:
        db_path = Path(directory) / "research.db"

        # ----------------------------------------------------
        # Real local LLM
        # ----------------------------------------------------

        provider = OllamaProvider(
            model="qwen3:4b",
            timeout_seconds=120,
            max_output_tokens=768,
        )

        planner = ResearchPlanner(provider)

        synthesizer = ResearchSynthesizer(
            provider=provider,
        )

        # ----------------------------------------------------
        # REAL ResearchRunner
        # ----------------------------------------------------

        runner = ResearchRunner(
            discoverer=FakeDiscoverer(),
            collector=FakeCollector(),
            extractor=FakeExtractor(),
            validator=ResearchValidator(),
        )

        executor = ResearchExecutor(
            runner=runner,
            max_attempts_per_step=1,
            min_sources_per_step=1,
        )

        # ----------------------------------------------------
        # Real persistence
        # ----------------------------------------------------

        store = ResearchStore(
            db_path,
        )

        # ----------------------------------------------------
        # Unified boundary
        # ----------------------------------------------------

        researcher = Researcher(
            planner=planner,
            executor=executor,
            synthesizer=synthesizer,
            store=store,
        )

        task = ResearchTask(
            name="phase17-e2e",
            question="What does the supplied evidence say about Python?",
            source_types=("web",),
            extraction_schema={
                "summary": "string",
            },
        )

        report = researcher.run(
            task,
            run_id="phase17-e2e-run",
        )

        # ----------------------------------------------------
        # Report contract
        # ----------------------------------------------------

        assert isinstance(
            report,
            ResearchReport,
        )

        report.validate()

        assert report.run_id == "phase17-e2e-run"

        assert report.question == task.question

        assert (
            report.execution.completed_steps >= 1
        )

        assert (
            report.execution.failed_steps == 0
        )

        assert (
            report.execution.completed_steps
            == len(report.execution.steps)
        )

        # ----------------------------------------------------
        # Synthesis contract
        # ----------------------------------------------------

        assert report.synthesis is not None

        assert (
            report.synthesis.sources_used == 1
        )

        assert len(
            report.synthesis.claims
        ) >= 1

        # ----------------------------------------------------
        # Persistence contract
        # ----------------------------------------------------

        counts = store.counts(
            "phase17-e2e-run",
        )

        assert counts == {
            "sources": 1,
            "evidence": 1,
            "claims": 1,
            "syntheses": 1,
        }

        assert store.get_run(
            "phase17-e2e-run",
        ) is not None

        print()
        print("REAL ResearchRunner: PASS")
        print(
            "completed_steps:",
            report.execution.completed_steps,
        )
        print(
            "sources:",
            counts["sources"],
        )
        print(
            "evidence:",
            counts["evidence"],
        )
        print(
            "claims:",
            counts["claims"],
        )
        print(
            "syntheses:",
            counts["syntheses"],
        )
        print(
            "answer:",
            report.synthesis.answer,
        )
