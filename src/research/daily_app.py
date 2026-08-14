from __future__ import annotations

from pathlib import Path

from .daily import (
    DDGSWebDiscoverer,
)
from .adapters.github_cli import GitHubCLIAdapter
from .adapters.jina import JinaWebAdapter
from .adapters.youtube_real import (
    YouTubeTranscriptAdapter,
)
from .agent_reach import (
    AgentReachCapabilityProvider,
)
from .reachability import SourceReachability
from .reachability_collector import (
    ReachabilitySourceCollector,
)
from .executor import ResearchExecutor
from .extractor import EvidenceExtractor
from .ollama import OllamaProvider
from .planner import ResearchPlanner
from .researcher import Researcher
from .runner import ResearchRunner
from .store import ResearchStore
from .synthesizer import ResearchSynthesizer
from .validator import ResearchValidator


def build_daily_researcher(
    *,
    model: str = "qwen3:4b",
    store_path: str | Path = "data/research/research.db",
    max_sources: int = 5,
) -> Researcher:
    """
    Construct the canonical daily-use research pipeline.

    This is the composition root.

    No production component constructs its own
    infrastructure dependency.
    """

    provider = OllamaProvider(
        model=model,
        timeout_seconds=120,
        max_output_tokens=768,
    )

    discoverer = DDGSWebDiscoverer(
        max_results=max_sources,
    )

    agent_reach = (
        AgentReachCapabilityProvider()
    )

    # Capability discovery is intentionally performed
    # outside the core collector contract. Agent Reach
    # determines which upstream channels are healthy;
    # existing adapters remain responsible for reading
    # and normalizing source content.

    capabilities = (
        agent_reach.snapshot()
    )

    reachability = SourceReachability(
        (
            GitHubCLIAdapter(),
            YouTubeTranscriptAdapter(),
            JinaWebAdapter(
                timeout_seconds=30.0,
                max_attempts=2,
                retry_delay_seconds=1.0,
            ),
        )
    )

    collector = ReachabilitySourceCollector(
        reachability,
    )

    runner = ResearchRunner(
        discoverer=discoverer,
        collector=collector,
        extractor=EvidenceExtractor(),
        validator=ResearchValidator(),
    )

    return Researcher(
        planner=ResearchPlanner(
            provider,
        ),
        executor=ResearchExecutor(
            runner=runner,
            max_attempts_per_step=2,
            min_sources_per_step=1,
        ),
        synthesizer=ResearchSynthesizer(
            provider,
        ),
        store=ResearchStore(
            store_path,
        ),
    )
