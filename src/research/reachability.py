from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReachabilityResult:
    """Normalized result returned by a source backend."""

    source_url: str
    content: str
    backend: str
    attempts: int

    def validate(self) -> None:
        if not self.source_url.strip():
            raise ValueError(
                "source_url must not be empty."
            )

        if not self.content.strip():
            raise ValueError(
                "content must not be empty."
            )

        if not self.backend.strip():
            raise ValueError(
                "backend must not be empty."
            )

        if self.attempts < 1:
            raise ValueError(
                "attempts must be >= 1."
            )


class SourceBackend(Protocol):
    """Minimal backend contract."""

    name: str

    def supports(self, source_url: str) -> bool:
        ...

    def read(self, source_url: str) -> ReachabilityResult:
        ...


@dataclass(frozen=True)
class BackendHealth:
    """Runtime health state for one backend."""

    name: str
    available: bool
    detail: str = ""

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "backend health name must not be empty."
            )


class SourceReachability:
    """
    Ordered multi-backend source resolver.

    The first supported backend that successfully returns
    content wins. Backend failures are isolated so one broken
    access path does not terminate the entire resolution process.
    """

    def __init__(
        self,
        backends: tuple[SourceBackend, ...],
    ) -> None:
        if not backends:
            raise ValueError(
                "At least one backend is required."
            )

        self.backends = backends

    def resolve(
        self,
        source_url: str,
    ) -> ReachabilityResult:
        if not source_url.strip():
            raise ValueError(
                "source_url must not be empty."
            )

        errors: list[str] = []
        attempts = 0

        for backend in self.backends:
            if not backend.supports(source_url):
                continue

            attempts += 1

            try:
                result = backend.read(source_url)
                result.validate()

                return ReachabilityResult(
                    source_url=result.source_url,
                    content=result.content,
                    backend=result.backend,
                    attempts=attempts,
                )

            except Exception as exc:
                errors.append(
                    f"{backend.name}: {exc}"
                )

        if errors:
            raise RuntimeError(
                "No reachable backend succeeded for "
                f"{source_url}. "
                + " | ".join(errors)
            )

        raise RuntimeError(
            "No backend supports source: "
            f"{source_url}"
        )

    def doctor(
        self,
    ) -> tuple[BackendHealth, ...]:
        """
        Return backend health information.

        Backends without an explicit health implementation are
        reported as available rather than executing arbitrary
        network operations.
        """

        results: list[BackendHealth] = []

        for backend in self.backends:
            health = getattr(
                backend,
                "health",
                None,
            )

            if callable(health):
                try:
                    value = health()

                    if isinstance(
                        value,
                        BackendHealth,
                    ):
                        value.validate()
                        results.append(value)
                        continue

                except Exception as exc:
                    results.append(
                        BackendHealth(
                            name=backend.name,
                            available=False,
                            detail=str(exc),
                        )
                    )
                    continue

            results.append(
                BackendHealth(
                    name=backend.name,
                    available=False,
                    detail="No health probe implemented.",
                )
            )

        return tuple(results)
