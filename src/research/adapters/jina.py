from __future__ import annotations

import time

import httpx

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class JinaWebAdapter:
    """
    Jina Reader-backed web adapter.

    Uses bounded retries for transient network failures.
    A failed attempt remains recoverable by the outer
    SourceReachability fallback layer.
    """

    name = "jina"

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        max_attempts: int = 2,
        retry_delay_seconds: float = 1.0,
        api_key: str | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be > 0."
            )

        if max_attempts < 1:
            raise ValueError(
                "max_attempts must be >= 1."
            )

        if retry_delay_seconds < 0:
            raise ValueError(
                "retry_delay_seconds must be >= 0."
            )

        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.retry_delay_seconds = (
            retry_delay_seconds
        )
        self.api_key = api_key

    def supports(
        self,
        source_url: str,
    ) -> bool:
        return source_url.startswith(
            ("http://", "https://")
        )

    def read(
        self,
        source_url: str,
    ) -> ReachabilityResult:

        headers = {
            "Accept": "text/plain",
        }

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        last_error: Exception | None = None

        for attempt in range(
            1,
            self.max_attempts + 1,
        ):
            try:
                response = httpx.get(
                    "https://r.jina.ai/"
                    + source_url,
                    headers=headers,
                    timeout=self.timeout_seconds,
                    follow_redirects=True,
                )

                response.raise_for_status()

                content = response.text.strip()

                if not content:
                    raise RuntimeError(
                        "Jina returned empty content."
                    )

                return ReachabilityResult(
                    source_url=source_url,
                    content=content,
                    backend=self.name,
                    attempts=attempt,
                )

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
            ) as exc:

                last_error = exc

                if (
                    attempt
                    < self.max_attempts
                    and self.retry_delay_seconds > 0
                ):
                    time.sleep(
                        self.retry_delay_seconds
                    )

            except httpx.HTTPStatusError as exc:
                raise RuntimeError(
                    "Jina returned HTTP "
                    f"{exc.response.status_code}."
                ) from exc

            except httpx.HTTPError as exc:
                raise RuntimeError(
                    f"Jina request failed: {exc}"
                ) from exc

        raise RuntimeError(
            "Jina request exhausted "
            f"{self.max_attempts} attempts: "
            f"{last_error}"
        )

    def health(self) -> BackendHealth:

        try:
            response = httpx.get(
                "https://r.jina.ai/",
                timeout=10.0,
                follow_redirects=True,
            )

            if response.status_code < 500:
                return BackendHealth(
                    name=self.name,
                    available=True,
                    detail=(
                        "Jina Reader endpoint reachable."
                    ),
                )

            return BackendHealth(
                name=self.name,
                available=False,
                detail=(
                    f"HTTP {response.status_code}"
                ),
            )

        except Exception as exc:
            return BackendHealth(
                name=self.name,
                available=False,
                detail=str(exc),
            )
