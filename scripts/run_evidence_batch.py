import json
from datetime import datetime, timezone
from pathlib import Path

from collector.evidence import create_evidence
from collector.web import fetch_webpage
from discovery.github import search_repositories
from models.profile import Confidence, SourceType
from storage import save_evidence_record


OUTPUT_DIR = Path("data/evidence")
REPORT_PATH = Path("data/research/evidence_batch_report.json")

TARGET_COUNT = 120

QUERIES = [
    "AI engineer",
    "generative AI engineer",
    "LLM engineer",
    "RAG engineer",
    "agentic AI",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_id(username: str, repository_name: str) -> str:
    raw = f"{username}-{repository_name}"

    allowed = set(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789-_"
    )

    return "".join(
        char if char in allowed else "_"
        for char in raw
    ).lower()


def discover_candidates():
    seen = set()
    candidates = []

    for query in QUERIES:

        print(f"\nDISCOVERY QUERY: {query}")

        results = search_repositories(
            query,
            per_page=30,
        )

        for candidate in results:

            key = (
                candidate.username.lower(),
                candidate.repository_url.lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            candidates.append(candidate)

            if len(candidates) >= TARGET_COUNT:
                return candidates

    return candidates


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n===== DISCOVERING CANDIDATES =====")

    candidates = discover_candidates()

    print(
        f"\nCandidates selected: {len(candidates)}"
    )

    if len(candidates) < TARGET_COUNT:
        raise RuntimeError(
            f"Expected {TARGET_COUNT} candidates, "
            f"found only {len(candidates)}"
        )

    report = {
        "started_at": utc_now(),
        "target_count": TARGET_COUNT,
        "candidate_count": len(candidates),
        "processed": 0,
        "succeeded": 0,
        "skipped": 0,
        "failed": 0,
        "failures": [],
        "records": [],
    }

    for index, candidate in enumerate(
        candidates[:TARGET_COUNT],
        start=1,
    ):

        evidence_id = safe_id(
            candidate.username,
            candidate.repository_name,
        )

        output_path = (
            OUTPUT_DIR
            / f"{evidence_id}.json"
        )

        print(
            f"\n[{index}/{TARGET_COUNT}] "
            f"{candidate.username}/{candidate.repository_name}"
        )

        # ----------------------------------------------------
        # RESUMABILITY
        # ----------------------------------------------------

        if output_path.exists():

            print(
                f"  SKIP — evidence already exists"
            )

            report["skipped"] += 1

            report["records"].append({
                "evidence_id": evidence_id,
                "username": candidate.username,
                "repository_name": candidate.repository_name,
                "repository_url": candidate.repository_url,
                "status": "skipped",
            })

            continue

        try:

            print("  Fetching repository page...")

            text = fetch_webpage(
                candidate.repository_url
            )

            if not text:
                raise RuntimeError(
                    "No usable webpage content extracted"
                )

            evidence = create_evidence(
                evidence_id=evidence_id,
                claim=(
                    "The GitHub repository page contains "
                    "publicly accessible project and "
                    "AI-engineering information."
                ),
                source_url=candidate.repository_url,
                source_type=SourceType.github_repository,
                evidence_text=text,
                confidence=Confidence.high,
            )

            path = save_evidence_record(
                evidence
            )

            report["processed"] += 1
            report["succeeded"] += 1

            report["records"].append({
                "evidence_id": evidence_id,
                "username": candidate.username,
                "repository_name": candidate.repository_name,
                "repository_url": candidate.repository_url,
                "status": "success",
                "characters": len(text),
                "path": str(path),
            })

            print(
                f"  PASS — {len(text)} characters"
            )

        except Exception as exc:

            report["processed"] += 1
            report["failed"] += 1

            failure = {
                "evidence_id": evidence_id,
                "username": candidate.username,
                "repository_name": candidate.repository_name,
                "repository_url": candidate.repository_url,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "failed_at": utc_now(),
            }

            report["failures"].append(
                failure
            )

            report["records"].append({
                "evidence_id": evidence_id,
                "username": candidate.username,
                "repository_name": candidate.repository_name,
                "repository_url": candidate.repository_url,
                "status": "failed",
            })

            print(
                f"  FAIL — {type(exc).__name__}: {exc}"
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

    print("\n============================================================")
    print(" EVIDENCE BATCH REPORT")
    print("============================================================")
    print(
        f"Candidates : {report['candidate_count']}"
    )
    print(
        f"Processed  : {report['processed']}"
    )
    print(
        f"Succeeded  : {report['succeeded']}"
    )
    print(
        f"Skipped    : {report['skipped']}"
    )
    print(
        f"Failed     : {report['failed']}"
    )
    print(
        f"Report     : {REPORT_PATH}"
    )

    if report["failed"] > 0:
        print(
            "\nWARNING: Some evidence records failed."
        )
        print(
            "Failures are isolated and saved in the report."
        )

    if (
        report["succeeded"]
        + report["skipped"]
        >= TARGET_COUNT
        and report["failed"] == 0
    ):
        print(
            "\nSTAGE 8B GREEN — "
            "120 VALID EVIDENCE RECORDS AVAILABLE"
        )


if __name__ == "__main__":
    main()
