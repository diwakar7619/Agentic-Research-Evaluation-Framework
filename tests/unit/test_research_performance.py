from research.performance import (
    PerformanceTimer,
    ResearchPerformance,
)


def test_performance_timer_records_stage():
    performance = ResearchPerformance()

    with PerformanceTimer(
        performance,
        "planning",
    ):
        pass

    assert len(performance.stages) == 1
    assert performance.stages[0].name == "planning"
    assert (
        performance.planning_seconds
        >= 0
    )


def test_performance_timer_populates_each_stage():
    performance = ResearchPerformance()

    with PerformanceTimer(
        performance,
        "execution",
    ):
        pass

    with PerformanceTimer(
        performance,
        "synthesis",
    ):
        pass

    with PerformanceTimer(
        performance,
        "persistence",
    ):
        pass

    assert (
        performance.execution_seconds
        >= 0
    )
    assert (
        performance.synthesis_seconds
        >= 0
    )
    assert (
        performance.persistence_seconds
        >= 0
    )


def test_research_performance_defaults():
    performance = ResearchPerformance()

    assert performance.total_seconds == 0.0
    assert performance.planning_seconds == 0.0
    assert performance.execution_seconds == 0.0
    assert performance.synthesis_seconds == 0.0
    assert performance.persistence_seconds == 0.0
    assert performance.sources_considered == 0
    assert performance.sources_collected == 0
    assert performance.completed_steps == 0
    assert performance.failed_steps == 0
