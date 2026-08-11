import json
from pathlib import Path
from datetime import datetime, timezone

from research.extractor import extract_profile
from research.tasks.ai_engineering import AI_ENGINEERING_PROFILE_RESEARCH


EVIDENCE_DIR = Path("data/evidence")
PROFILE_DIR = Path("data/research/profiles")
FAILURE_DIR = Path("data/research/failures")
REPORT_PATH = Path("data/research/batch_report.json")


PROFILE_DIR.mkdir(parents=True, exist_ok=True)
FAILURE_DIR.mkdir(parents=True, exist_ok=True)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    return "".join(
        char if char in allowed else "_"
        for char in value
    )


def main():
    evidence_files = sorted(
        EVIDENCE_DIR.rglob("*.json")
    )

    report = {
        "started_at": utc_now(),
        "total_evidence": len(evidence_files),
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "skipped": 0,
        "failures": [],
    }

    print(f"Evidence records: {len(evidence_files)}")

    for index, evidence_path in enumerate(
        evidence_files,
        start=1,
    ):

        try:
            evidence = json.loads(
                evidence_path.read_text(
                    encoding="utf-8"
                )
            )

            evidence_id = str(
                evidence.get(
                    "evidence_id",
                    evidence_path.stem,
                )
            )

            output_path = (
                PROFILE_DIR
                / f"{safe_name(evidence_id)}.json"
            )

            # ------------------------------------------------
            # RESUMABILITY
            # ------------------------------------------------

            if output_path.exists():
                print(
                    f"[{index}/{len(evidence_files)}] "
                    f"SKIP {evidence_id}"
                )

                report["skipped"] += 1
                continue

            print(
                f"[{index}/{len(evidence_files)}] "
                f"PROCESS {evidence_id}"
            )

            record = extract_profile(
                AI_ENGINEERING_PROFILE_RESEARCH,
                evidence,
            )

            output = {
                "profile_id": record.profile_id,
                "source_type": record.source_type,
                "source_url": record.source_url,
                "claim": record.claim,
                "confidence": record.confidence,
                "extracted": record.extracted,
                "retrieved_at": record.retrieved_at,
                "processed_at": utc_now(),
            }

            output_path.write_text(
                json.dumps(
                    output,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            report["processed"] += 1
            report["succeeded"] += 1

            print(
                f"    PASS -> {output_path.name}"
            )

        except Exception as exc:

            report["processed"] += 1
            report["failed"] += 1

            failure = {
                "evidence_file": str(evidence_path),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "failed_at": utc_now(),
            }

            report["failures"].append(failure)

            failure_path = (
                FAILURE_DIR
                / f"{safe_name(evidence_path.stem)}.json"
            )

            failure_path.write_text(
                json.dumps(
                    failure,
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            print(
                f"    FAIL -> {type(exc).__name__}: {exc}"
            )

    report["finished_at"] = utc_now()

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n===== BATCH REPORT =====")
    print(json.dumps(report, indent=2))

    if report["failed"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
