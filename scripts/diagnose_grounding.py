import json
import re
from pathlib import Path
from collections import Counter, defaultdict

REPORT_PATH = Path(
    "data/research/profile_grounding_report.json"
)

EVIDENCE_DIR = Path(
    "data/evidence"
)

OUTPUT_PATH = Path(
    "data/research/grounding_diagnostics.json"
)

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
        "retrieval",
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
        "tools",
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


def source_url(profile):
    return profile.get(
        "source_url",
        ""
    )


def find_evidence(profile):
    url = source_url(profile)

    for path in EVIDENCE_DIR.glob("*.json"):

        try:
            data = load_json(path)
        except Exception:
            continue

        if data.get("source_url") == url:
            return path

    return None


def context_windows(text, indicators):
    windows = []

    for indicator in indicators:

        start = 0

        while True:

            pos = text.find(
                indicator.lower(),
                start,
            )

            if pos == -1:
                break

            left = max(
                0,
                pos - 180,
            )

            right = min(
                len(text),
                pos + len(indicator) + 300,
            )

            windows.append(
                {
                    "indicator": indicator,
                    "context": text[left:right],
                }
            )

            start = (
                pos
                + len(indicator)
            )

            if len(windows) >= 8:
                return windows

    return windows


def main():

    report = load_json(
        REPORT_PATH
    )

    suspicious = report.get(
        "suspicious",
        []
    )

    field_counts = Counter()
    profile_counts = Counter()
    group_counts = Counter()

    suspicious_records = []

    for item in suspicious:

        if "field" not in item:
            continue

        field = item["field"]
        group = item["group"]
        profile_name = item["profile"]

        field_counts[field] += 1
        group_counts[group] += 1
        profile_counts[profile_name] += 1

        suspicious_records.append(item)

    # --------------------------------------------------------
    # Find evidence context for suspicious claims
    # --------------------------------------------------------

    enriched = []

    for item in suspicious_records:

        profile_path = (
            Path("data/research/profiles")
            / item["profile"]
        )

        if not profile_path.exists():
            continue

        profile = load_json(
            profile_path
        )

        evidence_path = find_evidence(
            profile
        )

        if evidence_path is None:

            enriched.append({
                **item,
                "evidence_found": False,
                "contexts": [],
            })

            continue

        evidence = load_json(
            evidence_path
        )

        text = normalize(
            evidence.get(
                "evidence_text",
                ""
            )
        )

        field = item["field"]

        contexts = context_windows(
            text,
            INDICATORS[field],
        )

        enriched.append({
            **item,
            "evidence_found": True,
            "evidence_file": (
                evidence_path.name
            ),
            "contexts": contexts,
        })

    # --------------------------------------------------------
    # Sort profiles by suspicious count
    # --------------------------------------------------------

    top_profiles = [
        {
            "profile": name,
            "suspicious_claims": count,
        }
        for name, count in
        profile_counts.most_common()
    ]

    # --------------------------------------------------------
    # Sort fields
    # --------------------------------------------------------

    top_fields = [
        {
            "field": name,
            "suspicious_claims": count,
        }
        for name, count in
        field_counts.most_common()
    ]

    # --------------------------------------------------------
    # Compact output
    # --------------------------------------------------------

    diagnostics = {
        "total_suspicious_claims": len(
            suspicious_records
        ),
        "by_group": dict(
            group_counts
        ),
        "by_field": top_fields,
        "top_profiles": top_profiles[:30],
        "claims": enriched,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            diagnostics,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Console report
    # --------------------------------------------------------

    print("\n============================================================")
    print(" SUSPICIOUS CLAIM DIAGNOSIS")
    print("============================================================")

    print(
        f"Total suspicious claims: "
        f"{len(suspicious_records)}"
    )

    print("\nBY GROUP")

    for group, count in group_counts.most_common():
        print(
            f"  {group:<22} {count}"
        )

    print("\nBY FIELD")

    for field, count in field_counts.most_common():
        print(
            f"  {field:<22} {count}"
        )

    print("\nTOP PROFILES")

    for item in top_profiles[:20]:
        print(
            f"  {item['suspicious_claims']:>2}  "
            f"{item['profile']}"
        )

    print("\n============================================================")
    print(" SAMPLE SUSPICIOUS CLAIMS + EVIDENCE CONTEXT")
    print("============================================================")

    for item in enriched[:20]:

        print(
            f"\n[{item['profile']}]"
        )

        print(
            f"  Claim: "
            f"{item.get('group')}."
            f"{item.get('field')} = "
            f"{item.get('value')}"
        )

        contexts = item.get(
            "contexts",
            []
        )

        if not contexts:

            print(
                "  Context: NO MATCHING INDICATOR"
            )

        else:

            for context in contexts[:2]:

                print(
                    f"  Indicator: "
                    f"{context['indicator']}"
                )

                print(
                    "  Context: "
                    + context["context"][:500]
                    .replace("\n", " ")
                )

    print("\n============================================================")
    print(" DIAGNOSTIC REPORT")
    print("============================================================")

    print(
        OUTPUT_PATH
    )

    print("\nNO QWEN EXTRACTION WAS RUN.")


if __name__ == "__main__":
    main()
