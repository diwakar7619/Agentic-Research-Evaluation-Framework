from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path

from research.crawler import (
    CrawlPolicy,
    ResearchCrawler,
)


async def run_smoke(
    url: str,
    lake: Path,
) -> None:

    crawler = ResearchCrawler(
        policy=CrawlPolicy(
            max_requests=1,
            max_depth=0,
            max_concurrency=1,
            max_requests_per_minute=10,
            allowed_domains=("127.0.0.1",),
            required_selector="#app",
            selector_timeout_seconds=5.0,
        ),
        lake_dir=lake,
    )

    result = await crawler.crawl([url])

    assert len(result.records) == 1

    record = result.records[0]

    expected = (
        "dynamic javascript research content "
        "loaded successfully."
    )

    assert expected in record.text.lower()

    assert result.data_path.exists()
    assert result.manifest_path.exists()

    print(
        "PASS: adaptive HTTP -> Playwright fallback"
    )
    print(
        "PASS: browser-rendered JavaScript content captured"
    )


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument("--root", required=True)
    parser.add_argument("--lake", required=True)
    parser.add_argument("--port", type=int, default=8766)

    args = parser.parse_args()

    root = Path(args.root).resolve()
    lake = Path(args.lake).resolve()

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tests.fixtures.crawler_server",
            "--root",
            str(root),
            "--port",
            str(args.port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:

        ready = False

        for _ in range(50):

            line = (
                server.stdout.readline()
                if server.stdout
                else ""
            )

            if (
                line
                and "fixture-server-ready"
                in line
            ):
                ready = True
                break

            time.sleep(0.1)

        if not ready:
            raise RuntimeError(
                "Fixture server did not start."
            )

        asyncio.run(
            run_smoke(
                (
                    f"http://127.0.0.1:"
                    f"{args.port}/dynamic.html"
                ),
                lake,
            )
        )

    finally:

        server.terminate()

        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
