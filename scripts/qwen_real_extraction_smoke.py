import json
from pathlib import Path

from extraction.qwen import extract_json


EVIDENCE_PATH = Path(
    "data/evidence/rohitg00-ai-engineering-from-scratch-source.json"
)


SCHEMA = {
    "type": "object",
    "properties": {
        "ai_capabilities": {
            "type": "object",
            "properties": {
                "llm_application": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "rag": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "embeddings": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "vector_database": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "agents": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "tool_calling": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "mcp": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
            },
            "required": [
                "llm_application",
                "rag",
                "embeddings",
                "vector_database",
                "agents",
                "tool_calling",
                "mcp",
            ],
        },
        "engineering_signals": {
            "type": "object",
            "properties": {
                "testing": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "ci_cd": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "docker": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "api_service": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
                "documentation": {
                    "type": "string",
                    "enum": ["true", "false", "unknown"],
                },
            },
            "required": [
                "testing",
                "ci_cd",
                "docker",
                "api_service",
                "documentation",
            ],
        },
    },
    "required": [
        "ai_capabilities",
        "engineering_signals",
    ],
}


evidence = json.loads(
    EVIDENCE_PATH.read_text(encoding="utf-8")
)

text = evidence["evidence_text"]

keywords = [
    "llm",
    "large language model",
    "rag",
    "retrieval",
    "embedding",
    "vector database",
    "vector store",
    "agent",
    "tool calling",
    "function calling",
    "mcp",
    "model context protocol",
    "testing",
    "tests",
    "ci/cd",
    "github actions",
    "docker",
    "fastapi",
    "api",
    "documentation",
]

lower_text = text.lower()
snippets = []
seen = set()

for keyword in keywords:
    start = 0

    while True:
        position = lower_text.find(keyword, start)

        if position == -1:
            break

        context_start = max(0, position - 400)
        context_end = min(len(text), position + 900)

        bucket = context_start // 500

        if bucket not in seen:
            snippets.append(text[context_start:context_end])
            seen.add(bucket)

        start = position + len(keyword)

        if len(snippets) >= 30:
            break

    if len(snippets) >= 30:
        break


relevant_evidence = "\n\n--- EVIDENCE SNIPPET ---\n\n".join(snippets)
relevant_evidence = relevant_evidence[:18000]


prompt = f"""
You are an evidence-based technical profile extraction system.

Analyze ONLY the supplied evidence.

Return ONLY the requested JSON object.

Do NOT summarize the repository.
Do NOT return repository metadata.
Do NOT copy commands.
Do NOT return links.
Do NOT add fields.

For every field:

- "true" means the evidence explicitly supports the capability.
- "false" means the evidence explicitly indicates absence.
- "unknown" means the evidence is insufficient.

Do not guess.
Do not use outside knowledge.

Required structure:

ai_capabilities:
- llm_application
- rag
- embeddings
- vector_database
- agents
- tool_calling
- mcp

engineering_signals:
- testing
- ci_cd
- docker
- api_service
- documentation

Evidence:

{relevant_evidence}
"""


result = extract_json(
    prompt,
    response_schema=SCHEMA,
)


expected_groups = {
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


for group, fields in expected_groups.items():
    if group not in result:
        raise ValueError(f"Missing output group: {group}")

    for field in fields:
        if field not in result[group]:
            raise ValueError(f"Missing output field: {group}.{field}")

        if result[group][field] not in {"true", "false", "unknown"}:
            raise ValueError(
                f"Invalid value for {group}.{field}: "
                f"{result[group][field]!r}"
            )


print(json.dumps(result, indent=2))
print("\nQWEN EXTRACTION CONTRACT: PASS")
