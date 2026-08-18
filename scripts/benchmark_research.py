from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


QUESTION = """Research the current state of production-grade AI agent engineering,
including reliable web research, retrieval, evidence extraction,
source validation, concurrency, caching, and scalable processing.

Focus on:
1. reliable web research,
2. retrieval and source selection,
3. evidence extraction,
4. source validation and provenance,
5. concurrency and performance,
6. caching and deduplication,
7. scalable processing.

Return concrete engineering practices supported by the gathered sources.
Stay strictly aligned with this research question.
"""


@dataclass
class BenchmarkRun:
    run_id: str
    requested_sources: int
    repetition: int
    warmup: bool
    exit_code: int
    wall_time_seconds: float
    planning_seconds: float | None = None
    execution_seconds: float | None = None
    synthesis_seconds: float | None = None
    persistence_seconds: float | None = None
    reported_total_seconds: float | None = None
    completed_steps: int | None = None
    failed_steps: int | None = None
    sources_considered: int | None = None
    sources_collected: int | None = None
    stdout_file: str = ""
    stderr_file: str = ""


def parse_performance(text: str) -> dict:
    patterns = {
        "planning_seconds": r"Planning:\s+([0-9.]+)\s*seconds?",
        "execution_seconds": r"Execution:\s+([0-9.]+)\s*seconds?",
        "synthesis_seconds": r"Synthesis:\s+([0-9.]+)\s*seconds?",
        "persistence_seconds": r"Persistence:\s+([0-9.]+)\s*seconds?",
        "reported_total_seconds": r"Total:\s+([0-9.]+)\s*seconds?",
        "completed_steps": r"Steps:\s+completed=(\d+)",
        "failed_steps": r"Steps:\s+completed=\d+,\s*failed=(\d+)",
        "sources_considered": r"Sources:\s+considered=(\d+)",
        "sources_collected": r"Sources:\s+considered=\d+,\s*collected=(\d+)",
    }

    result = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        value = match.group(1)

        if key.endswith("_seconds"):
            result[key] = float(value)
        else:
            result[key] = int(value)

    return result


def execute_run(
    *,
    run_id: str,
    requested_sources: int,
    repetition: int,
    warmup: bool,
    output_root: Path,
    model: str | None,
) -> BenchmarkRun:

    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = run_dir / "stdout.txt"
    stderr_path = run_dir / "stderr.txt"

    command = [
        sys.executable,
        "-m",
        "research.cli",
        "--sources",
        str(requested_sources),
        "--run-id",
        run_id,
    ]

    if model:
        command.extend(["--model", model])

    command.append(QUESTION)

    started = time.perf_counter()

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    wall_time = time.perf_counter() - started

    stdout_path.write_text(
        completed.stdout,
        encoding="utf-8",
    )

    stderr_path.write_text(
        completed.stderr,
        encoding="utf-8",
    )

    combined = completed.stdout + "\n" + completed.stderr
    metrics = parse_performance(combined)

    return BenchmarkRun(
        run_id=run_id,
        requested_sources=requested_sources,
        repetition=repetition,
        warmup=warmup,
        exit_code=completed.returncode,
        wall_time_seconds=wall_time,
        stdout_file=str(stdout_path),
        stderr_file=str(stderr_path),
        **metrics,
    )


def classify_runs(runs: list[dict]) -> tuple[list[dict], list[dict]]:
    """Classify non-warmup benchmark runs by actual research success."""

    successful = [
        run
        for run in runs
        if not run["warmup"]
        and run["exit_code"] == 0
        and run["failed_steps"] == 0
    ]

    failed = [
        run
        for run in runs
        if not run["warmup"]
        and (
            run["exit_code"] != 0
            or run["failed_steps"] != 0
        )
    ]

    return successful, failed


def main() -> int:

    parser = argparse.ArgumentParser(
        description="Controlled benchmark harness for the research engine."
    )

    parser.add_argument(
        "--levels",
        nargs="+",
        type=int,
        default=[5, 10, 25],
    )

    parser.add_argument(
        "--repetitions",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--warmup",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--model",
        default=None,
    )

    parser.add_argument(
        "--output",
        default="data/benchmarks",
    )

    args = parser.parse_args()

    if args.repetitions < 1:
        raise SystemExit("--repetitions must be >= 1")

    if any(level < 1 for level in args.levels):
        raise SystemExit("--levels must all be >= 1")

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    root = Path(args.output) / timestamp
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "timestamp_utc": timestamp,
        "question": QUESTION,
        "levels": args.levels,
        "repetitions": args.repetitions,
        "warmup_sources": args.warmup,
        "model": args.model,
        "python": sys.version,
        "runs": [],
    }

    print("=" * 60)
    print("RESEARCH BENCHMARK")
    print("=" * 60)
    print(f"Output: {root}")
    print(f"Levels: {args.levels}")
    print(f"Repetitions: {args.repetitions}")
    print()

    print("WARMUP")
    print("-" * 60)

    warmup_id = f"warmup-{timestamp}"

    warmup = execute_run(
        run_id=warmup_id,
        requested_sources=args.warmup,
        repetition=0,
        warmup=True,
        output_root=root,
        model=args.model,
    )

    manifest["runs"].append(asdict(warmup))

    print(
        f"exit={warmup.exit_code} "
        f"wall={warmup.wall_time_seconds:.3f}s"
    )

    if warmup.exit_code != 0:
        print("WARMUP FAILED. Benchmark aborted.")
        (root / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        return warmup.exit_code

    for level in args.levels:

        print()
        print("=" * 60)
        print(f"SOURCE LEVEL: {level}")
        print("=" * 60)

        for repetition in range(1, args.repetitions + 1):

            run_id = (
                f"benchmark-{timestamp}"
                f"-sources-{level}"
                f"-run-{repetition}"
            )

            print(
                f"Run {repetition}/{args.repetitions}: "
                f"{run_id}"
            )

            result = execute_run(
                run_id=run_id,
                requested_sources=level,
                repetition=repetition,
                warmup=False,
                output_root=root,
                model=args.model,
            )

            manifest["runs"].append(asdict(result))

            print(
                f"exit={result.exit_code} "
                f"wall={result.wall_time_seconds:.3f}s "
                f"reported_total="
                f"{result.reported_total_seconds}"
            )

            if result.exit_code != 0 or result.failed_steps != 0:
                print(
                    f"WARNING: {run_id} failed. "
                    f"exit_code={result.exit_code}, "
                    f"failed_steps={result.failed_steps}. "
                    "Continuing remaining repetitions."
                )

    manifest_path = root / "manifest.json"

    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"Manifest: {manifest_path}")
    print()

    successful, failed = classify_runs(manifest["runs"])

    print(f"Successful runs: {len(successful)}")
    print(f"Failed runs:     {len(failed)}")

    for level in args.levels:

        level_runs = [
            r
            for r in successful
            if r["requested_sources"] == level
        ]

        if not level_runs:
            print(
                f"{level} sources: NO SUCCESSFUL RUNS"
            )
            continue

        wall = [
            r["wall_time_seconds"]
            for r in level_runs
        ]

        print(
            f"{level} sources: "
            f"min={min(wall):.3f}s "
            f"max={max(wall):.3f}s "
            f"mean={sum(wall) / len(wall):.3f}s"
        )

    return 0 if not failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
