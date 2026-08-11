import json
from pathlib import Path

path = Path("data/evidence/rohitg00-ai-engineering-from-scratch-source.json")

data = json.loads(path.read_text(encoding="utf-8"))
text = data["evidence_text"]

keywords = [
    "RAG",
    "agent",
    "MCP",
    "embedding",
    "vector",
    "FastAPI",
    "Docker",
    "production",
    "project",
    "deployment",
]

for keyword in keywords:
    print(f"\n===== {keyword} =====")

    index = text.lower().find(keyword.lower())

    if index == -1:
        print("Not found")
        continue

    start = max(0, index - 500)
    end = min(len(text), index + 1500)

    print(text[start:end])
