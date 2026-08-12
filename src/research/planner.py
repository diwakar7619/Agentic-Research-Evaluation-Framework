from __future__ import annotations

from typing import Any

from research.plan import ResearchPlan, ResearchStep
from research.task import ResearchTask


PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "question": {"type": "string"},
                    "source_types": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "expected_evidence": {"type": "string"},
                    "priority": {
                        "type": "integer",
                        "minimum": 1,
                    },
                },
                "required": [
                    "id",
                    "question",
                    "source_types",
                    "expected_evidence",
                    "priority",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["steps"],
    "additionalProperties": False,
}


class ResearchPlanner:
    """
    Converts a research task into a bounded structured plan.

    Planning is provider-independent. The provider only generates
    structured data; execution remains outside the planner.
    """

    def __init__(
        self,
        provider,
        *,
        max_steps: int = 4,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be >= 1.")

        self.provider = provider
        self.max_steps = max_steps

    def plan(self, task: ResearchTask) -> ResearchPlan:
        task.validate()

        raw = self.provider.generate_json(
            prompt=self._build_prompt(task),
            schema=PLAN_SCHEMA,
        )

        plan = self._parse_plan(
            question=task.question,
            raw=raw,
            allowed_source_types=task.source_types,
        )

        plan.validate()
        return plan

    def _build_prompt(
        self,
        task: ResearchTask,
    ) -> str:
        allowed = ", ".join(task.source_types)

        return (
            "Create a research plan.\n"
            f"Question: {task.question}\n"
            f"Allowed sources: {allowed}\n"
            f"Maximum steps: {self.max_steps}\n\n"
            "For each step provide:\n"
            "- a concrete sub-question\n"
            "- allowed source types\n"
            "- expected evidence\n"
            "- priority\n\n"
            "Do not answer the question. "
            "Do not invent sources. "
            "Return only the requested JSON."
        )

    def _parse_plan(
        self,
        *,
        question: str,
        raw: dict[str, Any],
        allowed_source_types: tuple[str, ...],
    ) -> ResearchPlan:
        if not isinstance(raw, dict):
            raise ValueError(
                "Planner response must be an object."
            )

        raw_steps = raw.get("steps")

        if not isinstance(raw_steps, list):
            raise ValueError(
                "Planner response must contain a steps list."
            )

        if not raw_steps:
            raise ValueError(
                "Planner returned no research steps."
            )

        steps: list[ResearchStep] = []

        for index, item in enumerate(
            raw_steps[: self.max_steps],
            start=1,
        ):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Planner step {index} must be an object."
                )

            source_types = tuple(
                str(value)
                for value in item.get(
                    "source_types",
                    [],
                )
            )

            invalid_sources = [
                value
                for value in source_types
                if value not in allowed_source_types
            ]

            if invalid_sources:
                raise ValueError(
                    "Planner requested unsupported source types: "
                    + ", ".join(invalid_sources)
                )

            steps.append(
                ResearchStep(
                    id=str(
                        item.get(
                            "id",
                            f"step-{index}",
                        )
                    ),
                    question=str(
                        item.get(
                            "question",
                            "",
                        )
                    ),
                    source_types=source_types,
                    expected_evidence=str(
                        item.get(
                            "expected_evidence",
                            "",
                        )
                    ),
                    priority=int(
                        item.get(
                            "priority",
                            index,
                        )
                    ),
                )
            )

        return ResearchPlan(
            question=question,
            steps=tuple(steps),
        )
