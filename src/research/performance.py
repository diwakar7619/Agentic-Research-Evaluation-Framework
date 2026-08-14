from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import perf_counter
from typing import Any


@dataclass(frozen=True)
class PerformanceEvent:
    name: str
    duration_seconds: float
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ResearchPerformance:
    """
    Run-level performance telemetry.

    Worker threads record independent events.
    Aggregation happens after execution.

    This avoids relying on unsynchronised shared
    counters as the primary source of truth.
    """

    total_seconds: float = 0.0

    planning_seconds: float = 0.0
    execution_seconds: float = 0.0
    synthesis_seconds: float = 0.0
    persistence_seconds: float = 0.0

    events: list[PerformanceEvent] = field(
        default_factory=list
    )

    # Backward-compatible public stage contract.
    # Existing callers/tests use performance.stages.
    stages: list[PerformanceEvent] = field(
        default_factory=list
    )

    sources_considered: int = 0
    sources_collected: int = 0
    completed_steps: int = 0
    failed_steps: int = 0

    step_count: int = 0
    attempt_count: int = 0
    retry_count: int = 0

    configured_concurrency: int = 0
    peak_concurrency: int = 0

    llm_calls: int = 0
    llm_failures: int = 0

    llm_total_seconds: float = 0.0
    llm_load_seconds: float = 0.0
    llm_prompt_eval_seconds: float = 0.0
    llm_generation_seconds: float = 0.0

    llm_prompt_tokens: int = 0
    llm_output_tokens: int = 0

    prompt_characters: int = 0
    response_characters: int = 0

    task_runtime_seconds: float = 0.0

    _active_tasks: int = field(
        default=0,
        repr=False,
    )

    _lock: Lock = field(
        default_factory=Lock,
        repr=False,
    )

    def add_event(
        self,
        name: str,
        duration_seconds: float,
        **metadata: Any,
    ) -> None:
        event = PerformanceEvent(
            name=name,
            duration_seconds=duration_seconds,
            metadata=metadata,
        )

        with self._lock:
            self.events.append(event)

            # Preserve the existing stage-oriented API.
            self.stages.append(event)

    def begin_task(self) -> None:
        with self._lock:
            self._active_tasks += 1

            self.peak_concurrency = max(
                self.peak_concurrency,
                self._active_tasks,
            )

    def end_task(self) -> None:
        with self._lock:
            self._active_tasks = max(
                0,
                self._active_tasks - 1,
            )

    def record_step(
        self,
        *,
        duration_seconds: float,
        step_id: str,
        attempt: int,
        status: str,
        sources_collected: int = 0,
    ) -> None:
        with self._lock:
            self.step_count += 1
            self.attempt_count += 1
            self.task_runtime_seconds += (
                duration_seconds
            )

        self.add_event(
            "execution.step",
            duration_seconds,
            step_id=step_id,
            attempt=attempt,
            status=status,
            sources_collected=sources_collected,
        )

    def record_retry(self) -> None:
        with self._lock:
            self.retry_count += 1

    def record_llm(
        self,
        *,
        http_seconds: float,
        total_seconds: float,
        load_seconds: float,
        prompt_eval_seconds: float,
        generation_seconds: float,
        prompt_tokens: int,
        output_tokens: int,
        prompt_characters: int,
        response_characters: int,
        model: str,
    ) -> None:

        with self._lock:
            self.llm_calls += 1
            self.llm_total_seconds += total_seconds
            self.llm_load_seconds += load_seconds
            self.llm_prompt_eval_seconds += (
                prompt_eval_seconds
            )
            self.llm_generation_seconds += (
                generation_seconds
            )
            self.llm_prompt_tokens += prompt_tokens
            self.llm_output_tokens += output_tokens
            self.prompt_characters += prompt_characters
            self.response_characters += response_characters

        self.add_event(
            "llm.call",
            http_seconds,
            model=model,
            server_seconds=total_seconds,
            load_seconds=load_seconds,
            prompt_eval_seconds=prompt_eval_seconds,
            generation_seconds=generation_seconds,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
        )


class PerformanceTimer:
    def __init__(
        self,
        performance: ResearchPerformance,
        name: str,
        **metadata: Any,
    ) -> None:
        self.performance = performance
        self.name = name
        self.metadata = metadata
        self.started_at = 0.0

    def __enter__(self):
        self.started_at = perf_counter()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        duration = (
            perf_counter()
            - self.started_at
        )

        self.performance.add_event(
            self.name,
            duration,
            **self.metadata,
        )

        attribute = (
            f"{self.name}_seconds"
        )

        if hasattr(
            self.performance,
            attribute,
        ):
            setattr(
                self.performance,
                attribute,
                duration,
            )
