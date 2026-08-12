from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlsplit,
    urlunsplit,
)

from crawlee import ConcurrencySettings
from crawlee.crawlers import (
    AdaptivePlaywrightCrawler,
    AdaptivePlaywrightCrawlingContext,
)


DEFAULT_LAKE_DIR = Path("data/lake")


_TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
}


@dataclass(frozen=True)
class CrawlPolicy:
    """Explicit limits and safety rules for one research crawl."""

    max_requests: int = 25
    max_depth: int = 1
    max_concurrency: int = 3
    max_requests_per_minute: int = 60
    max_request_retries: int = 2
    request_timeout_seconds: float = 30.0
    allowed_domains: tuple[str, ...] = ()
    respect_robots_txt: bool = True

    # Adaptive rendering contract.
    required_selector: str | None = None
    selector_timeout_seconds: float = 5.0


@dataclass(frozen=True)
class CrawlRecord:
    """Normalized page-level record written to the research data lake."""

    url: str
    canonical_url: str
    title: str
    text: str
    retrieved_at: str
    content_hash: str
    depth: int


@dataclass(frozen=True)
class CrawlManifest:
    """Run-level metadata for reproducibility and auditing."""

    started_at: str
    finished_at: str
    requested_urls: tuple[str, ...]
    records_written: int
    unique_content_records: int


@dataclass(frozen=True)
class CrawlResult:
    """Complete result of one bounded crawl."""

    records: tuple[CrawlRecord, ...]
    manifest: CrawlManifest
    data_path: Path
    manifest_path: Path


def canonicalize_url(url: str) -> str:
    """Return a stable URL representation for identity/deduplication."""

    parts = urlsplit(url)

    query_pairs = [
        (key, value)
        for key, value in parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
        if (
            key.lower() not in _TRACKING_QUERY_KEYS
            and not key.lower().startswith("utm_")
        )
    ]

    query_pairs.sort()

    path = parts.path or "/"

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            urlencode(query_pairs),
            "",
        )
    )


def normalize_text(text: object) -> str:
    """Normalize parser output into stable plain text."""

    if text is None:
        return ""

    if hasattr(text, "get_text"):
        text = text.get_text(
            " ",
            strip=True,
        )
    elif not isinstance(text, str):
        text = str(text)

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def content_hash(text: str) -> str:
    """Create deterministic content identity."""

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def _allowed_url(
    url: str,
    allowed_domains: tuple[str, ...],
) -> bool:

    if not allowed_domains:
        return True

    hostname = urlsplit(url).hostname

    if not hostname:
        return False

    hostname = hostname.lower()

    return any(
        hostname == domain.lower()
        or hostname.endswith(
            "." + domain.lower()
        )
        for domain in allowed_domains
    )


class ResearchCrawler:
    """
    Bounded adaptive research crawler.

    Crawlee owns:
      - request queue
      - URL deduplication
      - retries
      - adaptive HTTP/browser execution
      - concurrency
      - crawl-depth control

    The project owns:
      - normalized research records
      - content identity
      - data-lake files
      - run manifest
    """

    def __init__(
        self,
        policy: CrawlPolicy | None = None,
        lake_dir: Path = DEFAULT_LAKE_DIR,
    ) -> None:

        self.policy = policy or CrawlPolicy()
        self.lake_dir = Path(lake_dir)

        self._records: list[CrawlRecord] = []
        self._seen_content_hashes: set[str] = set()

    def _build_crawler(
        self,
    ) -> AdaptivePlaywrightCrawler:

        concurrency = ConcurrencySettings(
            min_concurrency=1,
            desired_concurrency=min(
                self.policy.max_concurrency,
                3,
            ),
            max_concurrency=self.policy.max_concurrency,
            max_tasks_per_minute=(
                self.policy.max_requests_per_minute
            ),
        )

        crawler = (
            AdaptivePlaywrightCrawler
            .with_beautifulsoup_static_parser(
                max_requests_per_crawl=(
                    self.policy.max_requests
                ),
                max_crawl_depth=(
                    self.policy.max_depth
                ),
                max_request_retries=(
                    self.policy.max_request_retries
                ),
                request_handler_timeout=timedelta(
                    seconds=(
                        self.policy.request_timeout_seconds
                    )
                ),
                concurrency_settings=concurrency,
                respect_robots_txt_file=(
                    self.policy.respect_robots_txt
                ),
                playwright_crawler_specific_kwargs={
                    "headless": True,
                    "browser_type": "chromium",
                },
            )
        )

        @crawler.router.default_handler
        async def handler(
            context: AdaptivePlaywrightCrawlingContext,
        ) -> None:

            url = context.request.url

            if not _allowed_url(
                url,
                self.policy.allowed_domains,
            ):
                return

            # IMPORTANT:
            # If the selector is absent from the static HTTP response,
            # Crawlee automatically switches to Playwright and waits
            # for it. This is the documented adaptive contract.
            if self.policy.required_selector:
                parsed = await context.parse_with_static_parser(
                    selector=self.policy.required_selector,
                    timeout=timedelta(
                        seconds=(
                            self.policy.selector_timeout_seconds
                        )
                    ),
                )
            else:
                parsed = context.parsed_content

            title = normalize_text(
                parsed.title
                if getattr(parsed, "title", None)
                else ""
            )

            text = normalize_text(
                parsed.get_text(
                    " ",
                    strip=True,
                )
                if hasattr(parsed, "get_text")
                else getattr(parsed, "text", "")
            )

            if not text:
                return

            canonical_url = canonicalize_url(url)
            digest = content_hash(text)

            if digest in self._seen_content_hashes:
                return

            self._seen_content_hashes.add(digest)

            depth = int(
                context.request.user_data.get(
                    "depth",
                    0,
                )
            )

            self._records.append(
                CrawlRecord(
                    url=url,
                    canonical_url=canonical_url,
                    title=title,
                    text=text,
                    retrieved_at=(
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                    content_hash=digest,
                    depth=depth,
                )
            )

            if depth < self.policy.max_depth:

                await context.enqueue_links(
                    strategy="same-hostname",
                    user_data={
                        "depth": depth + 1,
                    },
                )

        return crawler

    async def crawl(
        self,
        urls: list[str],
    ) -> CrawlResult:

        if not urls:
            raise ValueError(
                "At least one URL is required."
            )

        self._records = []
        self._seen_content_hashes = set()

        started_at = datetime.now(
            timezone.utc
        ).isoformat()

        crawler = self._build_crawler()

        await crawler.run(urls)

        finished_at = datetime.now(
            timezone.utc
        ).isoformat()

        self.lake_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Microseconds prevent static + JS smoke runs from
        # overwriting each other when executed in the same second.
        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )

        data_path = (
            self.lake_dir
            / f"crawl_{timestamp}.jsonl"
        )

        manifest_path = (
            self.lake_dir
            / f"crawl_{timestamp}.manifest.json"
        )

        with data_path.open(
            "w",
            encoding="utf-8",
        ) as handle:

            for record in self._records:

                handle.write(
                    json.dumps(
                        asdict(record),
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        manifest = CrawlManifest(
            started_at=started_at,
            finished_at=finished_at,
            requested_urls=tuple(urls),
            records_written=len(
                self._records
            ),
            unique_content_records=len(
                self._seen_content_hashes
            ),
        )

        manifest_path.write_text(
            json.dumps(
                asdict(manifest),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return CrawlResult(
            records=tuple(
                self._records
            ),
            manifest=manifest,
            data_path=data_path,
            manifest_path=manifest_path,
        )
