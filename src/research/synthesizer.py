from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from research.execution import ResearchExecutionResult
from research.synthesis import (
    ResearchSynthesis,
    SynthesisClaim,
)


_SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
        },
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {
                        "type": "string",
                    },
                    "text": {
                        "type": "string",
                    },
                    "evidence_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "claim_id",
                    "text",
                    "evidence_ids",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "answer",
        "claims",
    ],
    "additionalProperties": False,
}


@dataclass
class ResearchSynthesizer:
    provider: Any

    def synthesize(
        self,
        execution: ResearchExecutionResult,
    ) -> ResearchSynthesis:
        execution.validate()

        evidence_map: dict[str, dict[str, str]] = {}

        for step_execution in execution.steps:
            if step_execution.result is None:
                continue

            for evidence in step_execution.result.evidence:
                evidence_map[evidence.source_id] = {
                    "source_id": evidence.source_id,
                    "source_url": evidence.source_url,
                    "text": evidence.text,
                }

        if not evidence_map:
            raise ValueError(
                "Cannot synthesize research without evidence."
            )

        evidence_block = "\n\n".join(
            (
                f"EVIDENCE_ID: {item['source_id']}\n"
                f"SOURCE: {item['source_url']}\n"
                f"TEXT:\n{item['text']}"
            )
            for item in evidence_map.values()
        )

        prompt = f"""
You are a research synthesis component.

Answer the research question using ONLY the supplied evidence.

Do not use outside knowledge.
Do not invent facts.
Do not invent evidence IDs.
Do not claim factual verification.
If evidence is insufficient, say so explicitly.

Every claim must reference one or more supplied evidence IDs.

Research question:
{execution.question}

Evidence:
{evidence_block}
""".strip()

        raw = self.provider.generate_json(
            prompt=prompt,
            schema=_SYNTHESIS_SCHEMA,
        )

        if not isinstance(raw, dict):
            raise ValueError(
                "Synthesis provider returned a non-object."
            )

        answer = raw.get("answer")

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError(
                "Synthesis answer is missing or empty."
            )

        raw_claims = raw.get("claims")

        if not isinstance(raw_claims, list):
            raise ValueError(
                "Synthesis claims must be a list."
            )

        claims: list[SynthesisClaim] = []

        for item in raw_claims:
            if not isinstance(item, dict):
                raise ValueError(
                    "Each synthesis claim must be an object."
                )

            claim_id = item.get("claim_id")
            text = item.get("text")
            evidence_ids = item.get("evidence_ids")

            if not isinstance(claim_id, str):
                raise ValueError(
                    "claim_id must be a string."
                )

            if not isinstance(text, str):
                raise ValueError(
                    "claim text must be a string."
                )

            if not isinstance(evidence_ids, list):
                raise ValueError(
                    "evidence_ids must be a list."
                )

            evidence_ids = tuple(evidence_ids)

            unknown = (
                set(evidence_ids)
                - set(evidence_map)
            )

            if unknown:
                raise ValueError(
                    "Synthesis referenced unknown evidence IDs: "
                    + ", ".join(sorted(unknown))
                )

            support_status = self._support_status(
                evidence_ids,
                execution,
            )

            claims.append(
                SynthesisClaim(
                    claim_id=claim_id,
                    text=text,
                    evidence_ids=evidence_ids,
                    support_status=support_status,
                )
            )

        result = ResearchSynthesis(
            question=execution.question,
            answer=answer.strip(),
            claims=tuple(claims),
            evidence_ids=tuple(evidence_map),
            sources_used=len(evidence_map),
        )

        result.validate()

        return result

    @staticmethod
    def _support_status(
        evidence_ids: tuple[str, ...],
        execution: ResearchExecutionResult,
    ) -> str:
        if not evidence_ids:
            return "insufficient"

        source_types: set[str] = set()

        for step_execution in execution.steps:
            if step_execution.result is None:
                continue

            for evidence in step_execution.result.evidence:
                if evidence.source_id in evidence_ids:
                    source_types.add(
                        step_execution.step.source_types[0]
                        if step_execution.step.source_types
                        else "unknown"
                    )

        if len(source_types) >= 2:
            return "corroborated"

        return "single_source"
