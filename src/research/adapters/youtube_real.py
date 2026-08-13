from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from research.reachability import (
    BackendHealth,
    ReachabilityResult,
)


class YouTubeTranscriptAdapter:
    """
    YouTube transcript backend using yt-dlp.

    Only subtitle/transcript extraction is performed.
    """

    name = "youtube-yt-dlp"

    def supports(
        self,
        source_url: str,
    ) -> bool:
        value = source_url.lower()

        return (
            "youtube.com/" in value
            or "youtu.be/" in value
        )

    def read(
        self,
        source_url: str,
    ) -> ReachabilityResult:
        executable = shutil.which("yt-dlp")

        if executable is None:
            raise RuntimeError(
                "yt-dlp is not installed."
            )

        with tempfile.TemporaryDirectory() as directory:
            output = (
                Path(directory)
                / "%(id)s"
            )

            command = [
                executable,
                "--write-sub",
                "--write-auto-sub",
                "--skip-download",
                "--sub-lang",
                "en,en-US,en-GB",
                "--sub-format",
                "vtt",
                "-o",
                str(output),
                source_url,
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    result.stderr.strip()
                    or "yt-dlp failed."
                )

            subtitle_files = list(
                Path(directory).glob("*.vtt")
            )

            if not subtitle_files:
                raise RuntimeError(
                    "No English transcript was available."
                )

            content = subtitle_files[0].read_text(
                encoding="utf-8",
                errors="replace",
            ).strip()

            if not content:
                raise RuntimeError(
                    "Transcript was empty."
                )

            return ReachabilityResult(
                source_url=source_url,
                content=content,
                backend=self.name,
                attempts=1,
            )

    def health(self) -> BackendHealth:
        executable = shutil.which(
            "yt-dlp"
        )

        if executable is None:
            return BackendHealth(
                name=self.name,
                available=False,
                detail="yt-dlp not found on PATH.",
            )

        try:
            result = subprocess.run(
                [
                    executable,
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
                        or "yt-dlp failed."
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
