import pytest

from research.task import ResearchTask
from research.tasks.ai_engineering import (
    AI_ENGINEERING_PROFILE_RESEARCH,
)


def test_research_task_validates():
    task = ResearchTask(
        name="example",
        question="What is being researched?",
        source_types=("github_repository", "web_page"),
        extraction_schema={"type": "object"},
    )

    task.validate()


def test_research_task_supports_source():
    task = ResearchTask(
        name="example",
        question="What is being researched?",
        source_types=("github_repository", "web_page"),
        extraction_schema={"type": "object"},
    )

    assert task.supports_source("github_repository")
    assert task.supports_source("web_page")
    assert not task.supports_source("pdf")


def test_empty_research_task_is_rejected():
    task = ResearchTask(
        name="",
        question="question",
        source_types=("github_repository",),
        extraction_schema={"type": "object"},
    )

    with pytest.raises(ValueError):
        task.validate()


def test_current_research_is_not_github_only():
    task = AI_ENGINEERING_PROFILE_RESEARCH

    task.validate()

    assert task.supports_source("github_repository")
    assert task.supports_source("web_page")
    assert task.supports_source("documentation")
    assert task.supports_source("pdf")


def test_current_research_has_extraction_schema():
    task = AI_ENGINEERING_PROFILE_RESEARCH

    properties = task.extraction_schema["properties"]

    assert "ai_capabilities" in properties
    assert "engineering_signals" in properties

