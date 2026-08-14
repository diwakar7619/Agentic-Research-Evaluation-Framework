from research.plan import ResearchPlan, ResearchStep
from research.planner import ResearchPlanner
from research.task import ResearchTask


class FakeProvider:
    def __init__(self, response):
        self.response = response
        self.prompt = None
        self.schema = None

    def generate_json(
        self,
        *,
        prompt,
        schema,
        performance=None,
    ):
        self.prompt = prompt
        self.schema = schema
        return self.response


def make_task():
    return ResearchTask(
        name="test",
        question="How does this project implement RAG?",
        source_types=(
            "github_repository",
            "web",
        ),
        extraction_schema={
            "type": "object",
        },
    )


def test_planner_builds_valid_plan():
    provider = FakeProvider(
        {
            "steps": [
                {
                    "id": "step-1",
                    "question": "Find the retrieval implementation.",
                    "source_types": ["github_repository"],
                    "expected_evidence": "Retriever and vector store code.",
                    "priority": 1,
                },
                {
                    "id": "step-2",
                    "question": "Find external documentation.",
                    "source_types": ["web"],
                    "expected_evidence": "Project documentation.",
                    "priority": 2,
                },
            ]
        }
    )

    planner = ResearchPlanner(provider)

    plan = planner.plan(make_task())

    assert isinstance(plan, ResearchPlan)
    assert len(plan.steps) == 2
    assert plan.steps[0].id == "step-1"
    assert provider.schema is not None


def test_planner_rejects_unsupported_source_type():
    provider = FakeProvider(
        {
            "steps": [
                {
                    "id": "step-1",
                    "question": "Search everywhere.",
                    "source_types": ["youtube"],
                    "expected_evidence": "Video evidence.",
                    "priority": 1,
                }
            ]
        }
    )

    planner = ResearchPlanner(provider)

    try:
        planner.plan(make_task())
    except ValueError as exc:
        assert "unsupported source types" in str(exc)
    else:
        raise AssertionError(
            "Expected unsupported source type to fail."
        )


def test_plan_rejects_duplicate_ids():
    plan = ResearchPlan(
        question="test",
        steps=(
            ResearchStep(
                id="same",
                question="one",
                source_types=("web",),
                expected_evidence="evidence",
            ),
            ResearchStep(
                id="same",
                question="two",
                source_types=("web",),
                expected_evidence="evidence",
            ),
        ),
    )

    try:
        plan.validate()
    except ValueError as exc:
        assert "Duplicate" in str(exc)
    else:
        raise AssertionError(
            "Expected duplicate IDs to fail."
        )
def test_planner_uses_normalized_step_question():
    provider = FakeProvider(
        {
            "steps": [
                {
                    "id": "step-1",
                    "question": "  Find the retrieval implementation.  ",
                    "source_types": ["github_repository"],
                    "expected_evidence": "Retriever implementation.",
                    "priority": 1,
                }
            ]
        }
    )

    planner = ResearchPlanner(provider)
    plan = planner.plan(make_task())

    assert plan.steps[0].question == "Find the retrieval implementation."


def test_planner_schema_restricts_source_types():
    provider = FakeProvider(
        {
            "steps": [
                {
                    "id": "step-1",
                    "question": "Find the retrieval implementation.",
                    "source_types": ["github_repository"],
                    "expected_evidence": "Retriever implementation.",
                    "priority": 1,
                }
            ]
        }
    )

    planner = ResearchPlanner(provider)
    planner.plan(make_task())

    schema = provider.schema
    allowed = (
        schema["properties"]["steps"]
        ["items"]["properties"]["source_types"]
        ["items"]["enum"]
    )

    assert allowed == ["github_repository", "web"]
