from .base import ResearchSourceAdapter
from .github import GitHubAdapter
from .github_cli import GitHubCLIAdapter
from .jina import JinaWebAdapter
from .web import WebAdapter
from .youtube import YouTubeAdapter
from .youtube_real import YouTubeTranscriptAdapter

__all__ = [
    "ResearchSourceAdapter",
    "GitHubAdapter",
    "GitHubCLIAdapter",
    "JinaWebAdapter",
    "WebAdapter",
    "YouTubeAdapter",
    "YouTubeTranscriptAdapter",
]
