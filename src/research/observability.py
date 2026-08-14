from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from time import perf_counter
from typing import Any, Iterator
import json
import os
import platform
import shutil
import subprocess
import uuid


_current_run: ContextVar[
    "TelemetryRun | None"
] = ContextVar(
    "research_telemetry_run",
    default=None,
)


def current_run() -> "TelemetryRun | None":
    """
    Return the telemetry run active in the current context.
    """
    return _current_run.get()


@dataclass
class _Span:
    name: str
    span_id: str
    parent_span_id: str | None
    started_at: float
    elapsed_seconds: float = 0.0
    success: bool = True
    attributes: dict[str, Any] = field(
        default_factory=dict
    )


class _SpanContext:

    def __init__(
        self,
        telemetry: "TelemetryRun",
        name: str,
        attributes: dict[str, Any],
    ) -> None:

        self.telemetry = telemetry
        self.name = name
        self.attributes = attributes
        self.span: _Span | None = None

    def __enter__(self) -> "_SpanContext":

        parent = (
            self.telemetry._span_stack[-1]
            if self.telemetry._span_stack
            else None
        )

        self.span = _Span(
            name=self.name,
            span_id=uuid.uuid4().hex,
            parent_span_id=(
                parent.span_id
                if parent is not None
                else None
            ),
            started_at=perf_counter(),
            attributes=dict(self.attributes),
        )

        self.telemetry._span_stack.append(
            self.span
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        if self.span is None:
            return

        self.span.elapsed_seconds = (
            perf_counter()
            - self.span.started_at
        )

        self.span.success = (
            exc_type is None
        )

        if self.telemetry._span_stack:
            self.telemetry._span_stack.pop()

        self.telemetry.spans.append(
            self.span
        )


class TelemetryRun:

    schema_version = "1.0"

    def __init__(
        self,
        run_id: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self.run_id = str(run_id)

        self.metadata = dict(
            metadata or {}
        )

        self.started_at = perf_counter()
        self.finished_at: float | None = None

        self.spans: list[_Span] = []
        self.events: list[dict[str, Any]] = []

        self.counters: dict[str, int] = {}
        self._histograms: dict[
            str,
            list[float],
        ] = {}

        self._span_stack: list[_Span] = []

        self._context_token = None

        self.system_start = self._system_snapshot()

    # --------------------------------------------------------
    # Context lifecycle
    # --------------------------------------------------------

    def __enter__(self) -> "TelemetryRun":

        self._context_token = _current_run.set(
            self
        )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.finish()

        if self._context_token is not None:

            _current_run.reset(
                self._context_token
            )

            self._context_token = None

    def finish(self) -> None:

        if self.finished_at is None:
            self.finished_at = perf_counter()

    # --------------------------------------------------------
    # Spans
    # --------------------------------------------------------

    def span(
        self,
        name: str,
        **attributes: Any,
    ) -> _SpanContext:

        return _SpanContext(
            self,
            name,
            attributes,
        )

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    def event(
        self,
        name: str,
        **attributes: Any,
    ) -> None:

        self.events.append(
            {
                "name": name,
                "timestamp": perf_counter(),
                "attributes": _jsonable(
                    attributes
                ),
            }
        )

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    def increment(
        self,
        name: str,
        value: int = 1,
    ) -> None:

        self.counters[name] = (
            self.counters.get(name, 0)
            + int(value)
        )

    # --------------------------------------------------------
    # Histograms
    # --------------------------------------------------------

    def observe(
        self,
        name: str,
        value: float,
    ) -> None:

        self._histograms.setdefault(
            name,
            [],
        ).append(
            float(value)
        )

    @staticmethod
    def _percentile(
        values: list[float],
        percentile: float,
    ) -> float:

        if not values:
            return 0.0

        ordered = sorted(values)

        if len(ordered) == 1:
            return ordered[0]

        position = (
            percentile
            / 100
            * (len(ordered) - 1)
        )

        lower = int(position)
        upper = min(
            lower + 1,
            len(ordered) - 1,
        )

        fraction = (
            position - lower
        )

        return (
            ordered[lower]
            + (
                ordered[upper]
                - ordered[lower]
            )
            * fraction
        )

    def _histogram_snapshot(
        self,
    ) -> dict[str, Any]:

        result: dict[str, Any] = {}

        for name, values in (
            self._histograms.items()
        ):

            result[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": (
                    sum(values)
                    / len(values)
                ),
                "p50": self._percentile(
                    values,
                    50,
                ),
                "p95": self._percentile(
                    values,
                    95,
                ),
                "p99": self._percentile(
                    values,
                    99,
                ),
            }

        return result

    # --------------------------------------------------------
    # System metrics
    # --------------------------------------------------------

    def _system_snapshot(
        self,
    ) -> dict[str, Any]:

        snapshot: dict[str, Any] = {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pid": os.getpid(),
            "cpu_count": os.cpu_count(),
        }

        try:

            import psutil

            process = psutil.Process(
                os.getpid()
            )

            snapshot["rss_mb"] = (
                process.memory_info().rss
                / 1024
                / 1024
            )

            snapshot["cpu_percent"] = (
                psutil.cpu_percent(
                    interval=None
                )
            )

        except Exception:

            snapshot["rss_mb"] = None
            snapshot["cpu_percent"] = None

        nvidia = shutil.which(
            "nvidia-smi"
        )

        if nvidia is None:

            snapshot["gpu"] = {
                "available": False
            }

            return snapshot

        try:

            command = [
                nvidia,
                "--query-gpu="
                "utilization.gpu,"
                "memory.used,"
                "memory.total,"
                "temperature.gpu",
                "--format=csv,noheader,nounits",
            ]

            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if (
                completed.returncode == 0
                and completed.stdout.strip()
            ):

                values = [
                    item.strip()
                    for item in
                    completed.stdout.split(",")
                ]

                if len(values) >= 4:

                    snapshot["gpu"] = {
                        "available": True,
                        "utilization_percent": float(
                            values[0]
                        ),
                        "memory_used_mb": float(
                            values[1]
                        ),
                        "memory_total_mb": float(
                            values[2]
                        ),
                        "temperature_c": float(
                            values[3]
                        ),
                    }

                    return snapshot

        except Exception:
            pass

        snapshot["gpu"] = {
            "available": False
        }

        return snapshot

    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:

        self.finish()

        duration = (
            self.finished_at
            - self.started_at
            if self.finished_at is not None
            else perf_counter()
            - self.started_at
        )

        return {
            "schema_version": self.schema_version,

            "trace": {
                "run_id": self.run_id,
                "duration_seconds": duration,
            },

            "metadata": _jsonable(
                self.metadata
            ),

            "spans": [
                {
                    "name": span.name,
                    "span_id": span.span_id,
                    "parent_span_id": (
                        span.parent_span_id
                    ),
                    "elapsed_seconds": (
                        span.elapsed_seconds
                    ),
                    "success": span.success,
                    "attributes": _jsonable(
                        span.attributes
                    ),
                }
                for span in sorted(
                    self.spans,
                    key=lambda item: item.started_at,
                )
            ],

            "events": _jsonable(
                self.events
            ),

            "metrics": {
                "counters": dict(
                    self.counters
                ),
                "histograms": (
                    self._histogram_snapshot()
                ),
            },

            "system": {
                "start": self.system_start,
                "end": self._system_snapshot(),
            },
        }

    # --------------------------------------------------------
    # JSON artifact
    # --------------------------------------------------------

    def write(
        self,
        directory: str | Path = (
            "data/telemetry"
        ),
    ) -> str:

        path = Path(directory)

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        output = (
            path
            / f"{self.run_id}.json"
        )

        output.write_text(
            json.dumps(
                self.snapshot(),
                indent=2,
                ensure_ascii=False,
                default=_jsonable,
            ),
            encoding="utf-8",
        )

        return str(output)


def _jsonable(value: Any) -> Any:

    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(
        value,
        Path,
    ):
        return str(value)

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key): _jsonable(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            _jsonable(item)
            for item in value
        ]

    return str(value)
