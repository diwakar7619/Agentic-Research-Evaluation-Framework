import json
import re
from pathlib import Path
from collections import Counter

EVIDENCE_DIR = Path("data/evidence")
PROFILE_DIR = Path("data/research/profiles")
REPORT_PATH = Path("data/research/profile_grounding_report.json")

# Conservative lexical indicators.
# Presence is NOT proof of a capability; absence is NOT proof of false.
INDICATORS = {
    "llm_application": [
        "llm",
        "large language model",
        "language model",
        "openai",
        "anthropic",
        "gemini",
        "ollama",
        "qwen",
        "chatgpt",
    ],
    "rag": [
        "rag",
        "retrieval augmented",
        "retrieval-augmented",
        "retrieval augmented generation",
    ],
    "embeddings": [
        "embedding",
        "embeddings",
        "text embedding",
        "vector embedding",
    ],
    "vector_database": [
        "vector database",
        "vector db",
        "vector store",
        "qdrant",
        "pinecone",
        "weaviate",
        "chroma",
        "milvus",
        "faiss",
    ],
    "agents": [
        "agent",
        "agents",
        "agentic",
        "multi-agent",
        "multi agent",
    ],
    "tool_calling": [
        "tool calling",
        "tool-calling",
        "function calling",
        "function-calling",
        "tool use",
        "tool-use",
    ],
    "mcp": [
        "mcp",
        "model context protocol",
        "model-context-protocol",
    ],
    "testing": [
        "test",
        "tests",
        "testing",
        "pytest",
        "unittest",
    ],
    "ci_cd": [
        "ci/cd",
        "ci cd",
        "continuous integration",
        "continuous deployment",
        "github actions",
        "gitlab ci",
        "jenkins",
    ],
    "docker": [
        "docker",
        "dockerfile",
        "container",
        "containers",
        "containerized",
    ],
    "api_service": [
        "api",
        "rest api",
        "restful",
        "fastapi",
        "flask",
        "endpoint",
        "endpoints",
    ],
    "documentation": [
        "documentation",
        "docs",
        "readme",
        "getting started",
        "installation",
        "usage",
    ],
}


def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        text.lower(),
    )


def load_json(path):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def find_evidence_for_profile(profile):
    source_url = profile.get("source_url", "")
    profile_id = profile.get("profile_id", "")

    candidates = []

    # Prefer exact source URL matching.
    for path in EVIDENCE_DIR.glob("*.json"):

        try:
            data = load_json(path)
        except Exception:
            continue

        if (
            data.get("source_url") == source_url
            or data.get("evidence_id") == profile_id
        ):
            candidates.append(path)

    if not candidates:
        return None

    return candidates[0]


def find_indicators(text, indicators):
    hits = []

    for indicator in indicators:
        if indicator.lower() in text:
            hits.append(indicator)

    return hits


def main():

    profiles = sorted(
        p
        for p in PROFILE_DIR.glob("*.json")
        if not p.stem.endswith("-source")
    )

    print(
        f"Batch profiles: {len(profiles)}"
    )

    audit_records = []

    totals = Counter()
    suspicious = []

    for index, profile_path in enumerate(
        profiles,
        start=1,
    ):

        profile = load_json(profile_path)

        evidence_path = find_evidence_for_profile(
            profile
        )

        if evidence_path is None:

            suspicious.append({
                "profile": profile_path.name,
                "reason": "matching evidence record not found",
            })

            continue

        evidence = load_json(
            evidence_path
        )

        evidence_text = normalize(
            evidence.get(
                "evidence_text",
                ""
            )
        )

        extracted = profile.get(
            "extracted",
            {}
        )

        record = {
            "profile": profile_path.name,
            "evidence": evidence_path.name,
            "fields": {},
        }

        for group, fields in {
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
        }.items():

            record["fields"][group] = {}

            for field in fields:

                value = extracted[group][field]

                indicators = INDICATORS[field]

                hits = find_indicators(
                    evidence_text,
                    indicators,
                )

                totals[
                    f"{field}:{value}"
                ] += 1

                field_result = {
                    "value": value,
                    "indicator_hits": hits,
                    "lexically_supported": (
                        len(hits) > 0
                    ),
                }

                record["fields"][group][field] = (
                    field_result
                )

                # Only flag TRUE values with no
                # lexical indicator.
                #
                # This is a suspicion signal,
                # not a semantic verdict.
                if (
                    value == "true"
                    and not hits
                ):

                    suspicious.append({
                        "profile": profile_path.name,
                        "group": group,
                        "field": field,
                        "value": value,
                        "reason": (
                            "true output has no "
                            "matching lexical indicator "
                            "in evidence"
                        ),
                    })

        audit_records.append(record)

        if index % 20 == 0:
            print(
                f"Audited {index}/{len(profiles)}"
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    true_fields = sum(
        count
        for key, count in totals.items()
        if key.endswith(":true")
    )

    true_supported = 0

    for record in audit_records:

        for group in record["fields"].values():

            for result in group.values():

                if (
                    result["value"] == "true"
                    and result["lexically_supported"]
                ):
                    true_supported += 1

    support_rate = (
        true_supported / true_fields
        if true_fields
        else 1.0
    )

    report = {
        "profiles_audited": len(profiles),
        "records_audited": len(audit_records),
        "true_field_count": true_fields,
        "lexically_supported_true_count": (
            true_supported
        ),
        "lexical_support_rate": support_rate,
        "suspicious_count": len(suspicious),
        "suspicious": suspicious,
        "value_counts": dict(totals),
        "records": audit_records,
        "limitations": [
            "Lexical indicator presence is not semantic proof.",
            "Indicator absence does not prove a capability is false.",
            "Generic terms such as 'agent', 'API', or 'test' may produce false lexical support.",
            "This stage identifies candidates for deeper review."
        ],
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n============================================================")
    print(" GROUNDING SUMMARY")
    print("============================================================")

    print(
        f"Profiles audited       : {len(profiles)}"
    )

    print(
        f"TRUE fields            : {true_fields}"
    )

    print(
        f"TRUE + lexical support : {true_supported}"
    )

    print(
        f"Lexical support rate   : "
        f"{support_rate:.1%}"
    )

    print(
        f"Suspicious TRUE claims : "
        f"{len(suspicious)}"
    )

    print(
        f"Report                 : "
        f"{REPORT_PATH}"
    )

    print("\n============================================================")
    print(" IMPORTANT")
    print("============================================================")

    print(
        "This is a grounding audit, NOT a semantic proof."
    )

    if suspicious:

        print(
            "\nSuspicious TRUE claims:"
        )

        for item in suspicious[:30]:

            print(
                f"  {item.get('profile')} | "
                f"{item.get('group')}."
                f"{item.get('field')} | "
                f"{item.get('reason')}"
            )

        if len(suspicious) > 30:
            print(
                f"  ... and "
                f"{len(suspicious) - 30} more"
            )

    else:

        print(
            "\nNo TRUE claims lacked lexical indicators."
        )

    print("\n============================================================")

    # We deliberately do NOT declare GREEN/RED from
    # lexical support alone.
    #
    # The output is an audit artifact for the next stage.

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
