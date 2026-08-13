from __future__ import annotations

import subprocess

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class GitHubCLIAdapter:
    """
    GitHub backend using the upstream gh CLI.

    This deliberately keeps GitHub access outside the research
    engine. The adapter only normalizes the result.
    """

    name = "github-gh"

    def supports(
        self,
        source_url: str,
    ) -> bool:
        return "github.com/" in source_url.lower()

    def read(
        self,
        source_url: str,
    ) -> ReachabilityResult:
        command = [
            "gh",
            "api",
            source_url.replace(
                "https://github.com/",
                "",
            ).rstrip("/"),
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
                or "gh command failed."
            )

        content = result.stdout.strip()

        if not content:
            raise RuntimeError(
                "gh returned empty content."
            )

        return ReachabilityResult(
            source_url=source_url,
            content=content,
            backend=self.name,
            attempts=1,
        )

    def health(self) -> BackendHealth:
        try:
            result = subprocess.run(
                [
                    "gh",
                    "--version",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                return BackendHealth(
                    name=self.name,
                    available=False,
                    detail=(
                        result.stderr.strip()
                        or "gh unavailable."
                    ),
                )

            return BackendHealth(
                name=self.name,
                available=True,
                detail=result.stdout.strip(),
            )

        except Exception as exc:
            return BackendHealth(
                name=self.name,
                available=False,
                detail=str(exc),
            )
