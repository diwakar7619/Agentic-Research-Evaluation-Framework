from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentReachChannel:
    """Normalized Agent Reach channel capability."""

    name: str
    available: bool
    backend: str | None = None
    detail: str = ""

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "Agent Reach channel name must not be empty."
            )


@dataclass(frozen=True)
class AgentReachCapabilities:
    """Snapshot of Agent Reach runtime capabilities."""

    available: bool
    version: str | None
    channels: tuple[AgentReachChannel, ...]

    def validate(self) -> None:
        names: set[str] = set()

        for channel in self.channels:
            channel.validate()

            if channel.name in names:
                raise ValueError(
                    f"Duplicate Agent Reach channel: {channel.name}"
                )

            names.add(channel.name)

    def supports(self, channel_name: str) -> bool:
        target = channel_name.strip().lower()

        return any(
            channel.name.lower() == target
            and channel.available
            for channel in self.channels
        )

    def channel_is_usable(
        self,
        channel_name: str,
    ) -> bool:
        """
        Return whether Agent Reach currently reports
        a usable backend for this channel.

        A warning channel is intentionally not treated
        as healthy unless Agent Reach reports an active
        backend.
        """
        target = channel_name.strip().lower()

        for channel in self.channels:
            if channel.name.lower() != target:
                continue

            return (
                channel.available
                and channel.backend is not None
            )

        return False

    def backend_for(
        self,
        channel_name: str,
    ) -> str | None:
        target = channel_name.strip().lower()

        for channel in self.channels:
            if channel.name.lower() == target:
                return channel.backend

        return None


class AgentReachCapabilityProvider:
    """
    Thin boundary around Agent Reach.

    Agent Reach remains responsible for installation,
    diagnostics and backend selection.

    This project only consumes normalized capabilities.
    """

    def __init__(
        self,
        *,
        executable: str = "agent-reach",
        timeout_seconds: float = 20.0,
    ) -> None:
        self.executable = executable
        self.timeout_seconds = timeout_seconds

    def available(self) -> bool:
        return (
            shutil.which(self.executable)
            is not None
        )

    def snapshot(self) -> AgentReachCapabilities:
        if not self.available():
            return AgentReachCapabilities(
                available=False,
                version=None,
                channels=(),
            )

        version = self._version()

        try:
            completed = subprocess.run(
                [
                    self.executable,
                    "doctor",
                    "--json",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
        except (
            OSError,
            subprocess.SubprocessError,
        ) as exc:
            return AgentReachCapabilities(
                available=True,
                version=version,
                channels=(),
            )

        if completed.returncode != 0:
            return AgentReachCapabilities(
                available=True,
                version=version,
                channels=(),
            )

        stdout = completed.stdout or ""

        try:
            payload = json.loads(
                stdout
            )
        except json.JSONDecodeError:
            return AgentReachCapabilities(
                available=True,
                version=version,
                channels=(),
            )

        channels = tuple(
            self._parse_channels(payload)
        )

        result = AgentReachCapabilities(
            available=True,
            version=version,
            channels=channels,
        )

        result.validate()

        return result

    def _version(self) -> str | None:
        try:
            completed = subprocess.run(
                [
                    self.executable,
                    "version",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
        except (
            OSError,
            subprocess.SubprocessError,
        ):
            return None

        if completed.returncode != 0:
            return None

        value = (
            completed.stdout.strip()
            or completed.stderr.strip()
        )

        return value or None

    def _parse_channels(
        self,
        payload: Any,
    ) -> list[AgentReachChannel]:
        channels: list[
            AgentReachChannel
        ] = []

        raw_channels = payload.get(
            "channels",
            {},
        ) if isinstance(payload, dict) else {}

        if not isinstance(
            raw_channels,
            dict,
        ):
            return channels

        for name, raw in raw_channels.items():
            if not isinstance(raw, dict):
                continue

            status = str(
                raw.get(
                    "status",
                    "",
                )
            ).strip().lower()

            available = status in {
                "available",
                "ok",
                "ready",
                "active",
            }

            backend = raw.get(
                "active_backend"
            )

            if backend is not None:
                backend = str(
                    backend
                ).strip() or None

            detail = str(
                raw.get(
                    "detail",
                    "",
                )
            ).strip()

            channels.append(
                AgentReachChannel(
                    name=str(name),
                    available=available,
                    backend=backend,
                    detail=detail,
                )
            )

        return channels
