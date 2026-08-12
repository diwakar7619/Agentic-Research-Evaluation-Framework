from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

from research.crawler import (
    CrawlPolicy,
    ResearchCrawler,
)


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        required=True,
    )

    parser.add_argument(
        "--lake",
        required=True,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8765,
    )

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

        policy = CrawlPolicy(
            max_requests=5,
            max_depth=1,
            max_concurrency=2,
            max_requests_per_minute=30,
            allowed_domains=(
                "127.0.0.1",
            ),
        )

        crawler = ResearchCrawler(
            policy=policy,
            lake_dir=lake,
        )

        result = asyncio.run(
            crawler.crawl(
                [
                    f"http://127.0.0.1:{args.port}/index.html"
                ]
            )
        )

        print(
            json.dumps(
                {
                    "records": len(
                        result.records
                    ),
                    "manifest": str(
                        result.manifest_path
                    ),
                    "data": str(
                        result.data_path
                    ),
                    "urls": [
                        record.canonical_url
                        for record in result.records
                    ],
                },
                indent=2,
            )
        )

        assert len(result.records) >= 2

        assert result.data_path.exists()
        assert result.manifest_path.exists()

        urls = {
            record.canonical_url
            for record in result.records
        }

        assert any(
            url.endswith(
                "/index.html"
            )
            for url in urls
        )

        assert any(
            url.endswith(
                "/page-two.html"
            )
            for url in urls
        )

        print(
            "PASS: static crawl + link discovery + data lake"
        )

    finally:

        server.terminate()

        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
