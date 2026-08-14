import json

from research.agent_reach import (
    AgentReachCapabilities,
    AgentReachCapabilityProvider,
    AgentReachChannel,
)


def test_capability_supports_available_channel():
    capabilities = AgentReachCapabilities(
        available=True,
        version="1.5.0",
        channels=(
            AgentReachChannel(
                name="github",
                available=True,
                backend="gh",
            ),
        ),
    )

    assert capabilities.supports("github")
    assert capabilities.backend_for("github") == "gh"


def test_capability_rejects_unavailable_channel():
    capabilities = AgentReachCapabilities(
        available=True,
        version="1.5.0",
        channels=(
            AgentReachChannel(
                name="reddit",
                available=False,
            ),
        ),
    )

    assert not capabilities.supports("reddit")


def test_provider_degrades_when_cli_missing():
    provider = AgentReachCapabilityProvider(
        executable="definitely-not-agent-reach"
    )

    result = provider.snapshot()

    assert result.available is False
    assert result.channels == ()


def test_provider_parses_doctor_payload(monkeypatch):
    provider = AgentReachCapabilityProvider()

    class Result:
        returncode = 0
        stdout = json.dumps(
            {
                "channels": {
                    "github": {
                        "status": "available",
                        "active_backend": "gh",
                    },
                    "youtube": {
                        "status": "available",
                        "active_backend": "yt-dlp",
                    },
                    "reddit": {
                        "status": "missing",
                    },
                }
            }
        )
        stderr = ""

    def fake_run(*args, **kwargs):
        return Result()

    monkeypatch.setattr(
        "research.agent_reach.shutil.which",
        lambda _: "agent-reach",
    )

    monkeypatch.setattr(
        "research.agent_reach.subprocess.run",
        fake_run,
    )

    result = provider.snapshot()

    assert result.available is True
    assert result.supports("github")
    assert result.backend_for("github") == "gh"
    assert result.supports("youtube")
    assert not result.supports("reddit")

def test_channel_is_usable_requires_active_backend():
    capabilities = AgentReachCapabilities(
        available=True,
        version="1.5.0",
        channels=(
            AgentReachChannel(
                name="github",
                available=True,
                backend="gh CLI",
            ),
            AgentReachChannel(
                name="youtube",
                available=False,
                backend="yt-dlp",
            ),
        ),
    )

    assert capabilities.channel_is_usable("github")
    assert not capabilities.channel_is_usable("youtube")
    assert not capabilities.channel_is_usable("reddit")

