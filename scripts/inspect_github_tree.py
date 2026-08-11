import json
from pathlib import Path

import httpx

REPO = "rohitg00/ai-engineering-from-scratch"

API_URL = f"https://api.github.com/repos/{REPO}/git/trees/main?recursive=1"

response = httpx.get(
    API_URL,
    headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-engineer-research/0.1",
    },
    timeout=30.0,
)

response.raise_for_status()

data = response.json()

files = [
    item["path"]
    for item in data["tree"]
    if item["type"] == "blob"
]

print(f"Total files: {len(files)}")

for path in files:
    if any(
        keyword in path.lower()
        for keyword in [
            "rag",
            "agent",
            "mcp",
            "embedding",
            "vector",
            "production",
            "api",
            "docker",
            "fastapi",
            "langgraph",
        ]
    ):
        print(path)
