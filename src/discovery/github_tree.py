import httpx

REPO = "rohitg00/ai-engineering-from-scratch"
BRANCH = "main"

MAX_RESULTS = 120

ALLOWED_EXTENSIONS = (
    ".md",
    ".json",
    ".py",
    ".ts",
    ".tsx",
    ".toml",
    ".yml",
    ".yaml",
    ".dockerfile",
)

EXCLUDED_PARTS = (
    "/certifications/",
    "/quiz.json",
    "/quizzes/",
    "/i18n/",
    "/node_modules/",
    "/.git/",
    "math-foundations/",
)

HIGH_VALUE_PREFIXES = (
    "phases/19-capstone-projects/",
    "phases/17-infrastructure-and-production/",
    "phases/16-multi-agent-and-swarms/",
    "phases/15-autonomous-systems/",
    "phases/14-agent-engineering/",
    "phases/13-tools-and-protocols/",
    "phases/11-llm-engineering/",
)

HIGH_VALUE_TERMS = (
    "rag",
    "agent",
    "mcp",
    "production",
    "observability",
    "deployment",
    "evaluation",
    "inference",
    "serving",
    "tool-use",
    "tool_call",
    "capstone",
)

LOW_VALUE_TERMS = (
    "quiz",
    "translation",
    "i18n",
    "exercise",
)


def _score_path(path: str) -> int:
    lower = path.lower()
    score = 0

    if lower == "readme.md":
        return 1000

    if lower.startswith(HIGH_VALUE_PREFIXES):
        score += 50

    if "/capstone-projects/" in lower:
        score += 30

    if "/outputs/" in lower:
        score += 20

    if "/docs/" in lower:
        score += 15

    if lower.endswith((
        "/readme.md",
        "/package.json",
        "/pyproject.toml",
        "/dockerfile",
    )):
        score += 25

    for term in HIGH_VALUE_TERMS:
        if term in lower:
            score += 5

    for term in LOW_VALUE_TERMS:
        if term in lower:
            score -= 30

    if "/tests/" in lower:
        score -= 5

    return score


def discover_relevant_files() -> list[str]:
    url = (
        f"https://api.github.com/repos/"
        f"{REPO}/git/trees/{BRANCH}?recursive=1"
    )

    response = httpx.get(
        url,
        headers={"User-Agent": "ai-engineer-research/0.1"},
        timeout=30.0,
    )

    response.raise_for_status()

    tree = response.json()["tree"]

    candidates = []

    for item in tree:
        path = item.get("path", "")
        lower = path.lower()

        if item.get("type") != "blob":
            continue

        if not lower.endswith(ALLOWED_EXTENSIONS):
            continue

        if any(part in lower for part in EXCLUDED_PARTS):
            continue

        score = _score_path(path)

        if score <= 0:
            continue

        candidates.append((score, path))

    candidates.sort(
        key=lambda item: (-item[0], item[1])
    )

    return [
        path
        for _, path in candidates[:MAX_RESULTS]
    ]


if __name__ == "__main__":
    files = discover_relevant_files()

    print(f"Relevant files found: {len(files)}")

    for path in files:
        print(path)
