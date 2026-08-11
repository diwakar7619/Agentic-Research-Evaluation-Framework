import json
from pathlib import Path
from collections import Counter

PROFILE_DIR = Path("data/research/profiles")

EXPECTED_GROUPS = {
    "ai_capabilities": [
        "llm_application",
        "rag",
        "embeddings",
        "vector_database",
        "agents",
        "tool_calling",
        "mcp",
    ],
    "engineering_signals": [
        "testing",
        "ci_cd",
        "docker",
        "api_service",
        "documentation",
    ],
}

VALID_VALUES = {"true", "false", "unknown"}


def is_seed_profile(path: Path) -> bool:
    return path.stem.endswith("-source")


def validate_profile(path: Path):
    errors = []

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        return [f"invalid JSON: {exc}"]

    extracted = data.get("extracted")

    if not isinstance(extracted, dict):
        return ["missing or invalid 'extracted' object"]

    for group, fields in EXPECTED_GROUPS.items():

        if group not in extracted:
            errors.append(
                f"missing group: extracted.{group}"
            )
            continue

        if not isinstance(extracted[group], dict):
            errors.append(
                f"extracted.{group} must be an object"
            )
            continue

        for field in fields:

            if field not in extracted[group]:
                errors.append(
                    f"missing field: extracted.{group}.{field}"
                )
                continue

            value = extracted[group][field]

            if value not in VALID_VALUES:
                errors.append(
                    f"invalid value: "
                    f"extracted.{group}.{field}={value!r}"
                )

    return errors


def main():

    files = sorted(
        PROFILE_DIR.glob("*.json")
    )

    batch_files = [
        path
        for path in files
        if not is_seed_profile(path)
    ]

    seed_files = [
        path
        for path in files
        if is_seed_profile(path)
    ]

    print(
        f"Total profile files : {len(files)}"
    )

    print(
        f"Batch profiles      : {len(batch_files)}"
    )

    print(
        f"Seed profiles       : {len(seed_files)}"
    )

    valid = 0
    invalid = 0
    failures = []

    value_counts = {
        group: {
            field: Counter()
            for field in fields
        }
        for group, fields in EXPECTED_GROUPS.items()
    }

    for path in batch_files:

        errors = validate_profile(path)

        if errors:

            invalid += 1

            failures.append({
                "file": path.name,
                "errors": errors,
            })

            continue

        valid += 1

        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        extracted = data["extracted"]

        for group, fields in EXPECTED_GROUPS.items():
            for field in fields:
                value_counts[group][field][
                    extracted[group][field]
                ] += 1

    print("\n============================================================")
    print(" PROFILE VALIDATION")
    print("============================================================")

    print(f"Valid   : {valid}")
    print(f"Invalid : {invalid}")

    print("\n============================================================")
    print(" VALUE DISTRIBUTION")
    print("============================================================")

    for group, fields in EXPECTED_GROUPS.items():

        print(f"\n[{group}]")

        for field in fields:

            counts = value_counts[group][field]

            print(
                f"  {field:<20} "
                f"true={counts['true']:>3} "
                f"false={counts['false']:>3} "
                f"unknown={counts['unknown']:>3}"
            )

    report = {
        "total_files": len(files),
        "batch_profiles": len(batch_files),
        "seed_profiles": len(seed_files),
        "valid": valid,
        "invalid": invalid,
        "failures": failures,
        "value_distribution": {
            group: {
                field: dict(
                    value_counts[group][field]
                )
                for field in fields
            }
            for group, fields in EXPECTED_GROUPS.items()
        },
    }

    report_path = Path(
        "data/research/profile_quality_report.json"
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\nReport: {report_path}"
    )

    if failures:

        print("\n============================================================")
        print(" INVALID PROFILES")
        print("============================================================")

        for failure in failures:

            print(
                f"\n{failure['file']}"
            )

            for error in failure["errors"]:
                print(f"  - {error}")

    print("\n============================================================")

    if (
        len(batch_files) == 120
        and valid == 120
        and invalid == 0
    ):

        print(" STAGE 8D GREEN")
        print(" 120/120 profiles satisfy extraction contract.")
        return 0

    print(" STAGE 8D NOT GREEN")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
