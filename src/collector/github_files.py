from pathlib import Path

import httpx


RAW_DIR = Path("data/raw/github")
RAW_DIR.mkdir(parents=True, exist_ok=True)

REPO = "rohitg00/ai-engineering-from-scratch"
BRANCH = "main"

TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=15.0,
    write=5.0,
    pool=5.0,
)


def fetch_github_file(path: str) -> str:
    url = (
        f"https://raw.githubusercontent.com/"
        f"{REPO}/{BRANCH}/{path}"
    )

    response = httpx.get(
        url,
        headers={"User-Agent": "ai-engineer-research/0.1"},
        timeout=TIMEOUT,
        follow_redirects=True,
    )

    response.raise_for_status()

    return response.text


def save_github_file(path: str) -> Path:
    output = RAW_DIR / path.replace("/", "__")

    # Don't download something we already have.
    if output.exists():
        return output

    content = fetch_github_file(path)

    output.write_text(
        content,
        encoding="utf-8",
    )

    return output
