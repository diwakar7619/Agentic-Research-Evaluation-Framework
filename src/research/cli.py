from __future__ import annotations

import argparse
import json
import time
import uuid

from .daily_app import build_daily_researcher
from .task import ResearchTask


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="research",
        description=(
            "Evidence-grounded local research "
            "using the canonical research engine."
        ),
    )

    parser.add_argument(
        "question",
        help="Research question to investigate.",
    )

    parser.add_argument(
        "--sources",
        type=int,
        default=5,
        help="Maximum web sources per research step.",
    )

    parser.add_argument(
        "--model",
        default="qwen3:4b",
        help="Local Ollama model.",
    )

    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional persistent run identifier.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete report as JSON.",
    )

    return parser


def main(
    argv: list[str] | None = None,
) -> int:

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.sources < 1:
        parser.error(
            "--sources must be at least 1."
        )

    run_id = (
        args.run_id
        or f"research-{uuid.uuid4().hex[:12]}"
    )

    task = ResearchTask(
        name="daily-research",
        question=args.question,
        source_types=("web",),
        extraction_schema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                },
                "summary": {
                    "type": "string",
                },
            },
            "required": [
                "status",
                "summary",
            ],
            "additionalProperties": False,
        },
        metadata={
            "max_sources": args.sources,
        },
    )

    researcher = build_daily_researcher(
        model=args.model,
        max_sources=args.sources,
    )

    print(
        f"Research run: {run_id}"
    )
    print(
        f"Question: {task.question}"
    )
    print()

    started_at = time.perf_counter()

    report = researcher.run(
        task,
        run_id=run_id,
    )

    elapsed_seconds = (
        time.perf_counter() - started_at
    )

    if args.json:

        payload = {
            "run_id": report.run_id,
            "question": report.question,
            "answer": report.synthesis.answer,
            "sources_used": (
                report.synthesis.sources_used
            ),
            "elapsed_seconds": round(
                elapsed_seconds,
                3,
            ),
            "claims": [
                {
                    "claim_id": claim.claim_id,
                    "text": claim.text,
                    "evidence_ids": list(
                        claim.evidence_ids
                    ),
                    "support_status": (
                        claim.support_status
                    ),
                }
                for claim in report.synthesis.claims
            ],
        }

        print(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            )
        )

        return 0

    print("============================================================")
    print("RESEARCH RESULT")
    print("============================================================")
    print()
    print(report.synthesis.answer)
    print()
    print(
        f"Sources used: "
        f"{report.synthesis.sources_used}"
    )

    print(
        f"Research time: "
        f"{elapsed_seconds:.3f} seconds"
    )

    print()

    print("CLAIMS")
    print("------")

    for claim in report.synthesis.claims:

        print()
        print(
            f"[{claim.claim_id}] "
            f"{claim.support_status}"
        )
        print(claim.text)
        print(
            "Evidence:",
            ", ".join(
                claim.evidence_ids
            ),
        )

    performance = researcher.last_performance

    print()
    print("PERFORMANCE")
    print("-----------")
    print(
        f"Planning:    "
        f"{performance.planning_seconds:.3f} seconds"
    )
    print(
        f"Execution:   "
        f"{performance.execution_seconds:.3f} seconds"
    )
    print(
        f"Synthesis:   "
        f"{performance.synthesis_seconds:.3f} seconds"
    )
    print(
        f"Persistence: "
        f"{performance.persistence_seconds:.3f} seconds"
    )
    print(
        f"Total:       "
        f"{performance.total_seconds:.3f} seconds"
    )
    print(
        f"Steps:       "
        f"completed={performance.completed_steps}, "
        f"failed={performance.failed_steps}"
    )
    print(
        f"Sources:     "
        f"considered={performance.sources_considered}, "
        f"collected={performance.sources_collected}"
    )

    print()
    print(
        f"Run ID: {report.run_id}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
