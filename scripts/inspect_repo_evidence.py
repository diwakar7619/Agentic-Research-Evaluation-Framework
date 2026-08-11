import json
from pathlib import Path

path = Path("data/evidence/rohitg00-ai-engineering-from-scratch-source.json")

data = json.loads(path.read_text(encoding="utf-8"))
text = data["evidence_text"]

keywords = [
    "github.com/rohitg00/ai-engineering-from-scratch/tree",
    "phases/",
    "projects/",
    "code/",
    "outputs/",
    "FastAPI",
    "LangGraph",
    "LangChain",
    "Qdrant",
    "Chroma",
    "PostgreSQL",
    "MCP server",
]

for keyword in keywords:
    print(f"\n===== {keyword} =====")

    start_at = 0
    found = 0

    while found < 3:
        index = text.lower().find(keyword.lower(), start_at)

        if index == -1:
            break

        start = max(0, index - 300)
        end = min(len(text), index + 1200)

        print(text[start:end])
        print("\n---\n")

        start_at = index + len(keyword)
        found += 1
