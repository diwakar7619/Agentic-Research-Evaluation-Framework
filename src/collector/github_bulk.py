from pathlib import Path

from collector.github_files import fetch_github_file
from discovery.github_tree import discover_relevant_files

RAW_DIR = Path("data/raw/github")


def collect_relevant_files() -> list[Path]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    saved = []

    for path in discover_relevant_files():
        output = RAW_DIR / path.replace("/", "__")

        if output.exists():
            saved.append(output)
            continue

        content = fetch_github_file(path)
        output.write_text(content, encoding="utf-8")
        saved.append(output)

    return saved
