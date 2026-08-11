from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProfileRecord:
    """
    Normalized result for one researched technical profile.

    Evidence/provenance stays attached to the extracted result so
    downstream analysis can always trace a claim back to its source.
    """

    profile_id: str
    source_type: str
    source_url: str
    claim: str
    confidence: str
    extracted: dict[str, Any]
    retrieved_at: str

    def validate(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("profile_id cannot be empty.")

        if not self.source_type.strip():
            raise ValueError("source_type cannot be empty.")

        if not self.source_url.strip():
            raise ValueError("source_url cannot be empty.")

        if not isinstance(self.extracted, dict):
            raise TypeError("extracted must be a dictionary.")

        if not self.extracted:
            raise ValueError("extracted cannot be empty.")
