from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Iterator


@dataclass
class StageMetric:
    name: str
    started_at: float
    elapsed_seconds: float = 0.0
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchTelemetry:
    run_id: str
    stages: list[StageMetric] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=dict)

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def record_stage(
        self,
        name: str,
        elapsed_seconds: float,
        *,
        success: bool = True,
        **metadata: Any,
    ) -> None:
        self.stages.append(
            StageMetric(
                name=name,
                started_at=perf_counter() - elapsed_seconds,
                elapsed_seconds=elapsed_seconds,
                success=success,
                metadata=metadata,
            )
        )

    @contextmanager
    def stage(
        self,
        name: str,
        **metadata: Any,
    ) -> Iterator[None]:
        started = perf_counter()
        success = False

        try:
            yield
            success = True
        finally:
            self.record_stage(
                name,
                perf_counter() - started,
                success=success,
                **metadata,
            )

    def summary(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "counters": dict(self.counters),
            "stages": [
                {
                    "name": stage.name,
                    "elapsed_seconds": round(
                        stage.elapsed_seconds,
                        4,
                    ),
                    "success": stage.success,
                    "metadata": stage.metadata,
                }
                for stage in self.stages
            ],
        }
def system_snapshot() -> dict[str, object]:
    """
    Lightweight process/GPU snapshot.

    This intentionally captures only run-boundary state.
    Continuous polling is unnecessary for the first
    performance investigation and would add measurement
    overhead.
    """

    import os
    import platform
    import shutil
    import subprocess

    result: dict[str, object] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pid": os.getpid(),
        "cpu_count": os.cpu_count(),
    }

    try:
        import resource

        rss = resource.getrusage(
            resource.RUSAGE_SELF
        ).ru_maxrss

        if rss > 1024 * 1024:
            rss_mb = rss / 1024 / 1024
        else:
            rss_mb = rss / 1024

        result["rss_mb"] = rss_mb

    except Exception:
        result["rss_mb"] = None

    nvidia = shutil.which("nvidia-smi")

    if nvidia is None:
        result["gpu"] = {
            "available": False,
        }

        return result

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

        if completed.returncode != 0:
            result["gpu"] = {
                "available": False,
            }

            return result

        values = [
            value.strip()
            for value in completed.stdout.split(",")
        ]

        if len(values) >= 4:

            result["gpu"] = {
                "available": True,
                "utilization_percent": float(values[0]),
                "memory_used_mb": float(values[1]),
                "memory_total_mb": float(values[2]),
                "temperature_c": float(values[3]),
            }

        else:

            result["gpu"] = {
                "available": False,
            }

    except Exception:

        result["gpu"] = {
            "available": False,
        }

    return result
