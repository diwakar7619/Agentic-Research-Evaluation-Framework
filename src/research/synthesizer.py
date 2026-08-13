from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
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
    max_quality_retries: int = field(
        default=1,
        kw_only=True,
    )

    provider: Any

    @staticmethod
    def _build_synthesis_schema(
        evidence_ids: tuple[str, ...],
    ) -> dict[str, object]:
        if not evidence_ids:
            raise ValueError(
                "At least one evidence ID is required."
            )

        schema = deepcopy(_SYNTHESIS_SCHEMA)

        schema["properties"]["claims"]["items"][
            "properties"
        ]["evidence_ids"]["items"] = {
            "type": "string",
            "enum": list(evidence_ids),
        }

        return schema

    def synthesize(
        self,
        execution: ResearchExecutionResult,
    ) -> ResearchSynthesis:
        execution.validate()

        if self.max_quality_retries < 0:
            raise ValueError(
                "max_quality_retries must be >= 0."
            )

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

Answer the research question directly using ONLY the supplied evidence.

Focus the answer on what the question actually asks.
Do not answer a broader or different question.
Do not introduce tangential comparisons, products, companies,
or background topics unless they directly help answer the question.

Do not use outside knowledge.
Do not invent facts.
Do not invent evidence IDs.
Do not claim factual verification.
If evidence is insufficient, say so explicitly.

Every claim must reference one or more supplied evidence IDs.

Valid evidence IDs:
{", ".join(evidence_map.keys())}

Use ONLY the exact evidence IDs listed above.
Do not create, rename, normalize, or infer evidence IDs.

Research question:
{execution.question}

Evidence:
{evidence_block}
""".strip()

        valid_evidence_ids = tuple(
            evidence_map.keys()
        )

        synthesis_schema = (
            self._build_synthesis_schema(
                valid_evidence_ids
            )
        )

        raw = None
        quality_error: ValueError | None = None

        for attempt in range(
            self.max_quality_retries + 1
        ):
            current_prompt = prompt

            if quality_error is not None:
                current_prompt = (
                    prompt
                    + "\n\nQUALITY FAILURE FROM PREVIOUS "
                    "ATTEMPT:\n"
                    + str(quality_error)
                    + "\n\n"
                    "Rewrite the answer so that it directly "
                    "answers the research question. "
                    "Do not describe the user, the task, "
                    "the prompt, or the supplied material. "
                    "Return only the requested JSON."
                )

            raw = self.provider.generate_json(
                prompt=current_prompt,
                schema=synthesis_schema,
            )

            if not isinstance(raw, dict):
                quality_error = ValueError(
                    "Synthesis provider returned a non-object."
                )
                continue

            answer = raw.get("answer")

            if (
                not isinstance(answer, str)
                or not answer.strip()
            ):
                quality_error = ValueError(
                    "Synthesis answer is missing or empty."
                )
                continue

            try:
                self._validate_answer_quality(
                    answer,
                    execution.question,
                )
            except ValueError as exc:
                quality_error = exc
                continue

            quality_error = None
            break

        if quality_error is not None:
            raise quality_error

        if raw is None:
            raise ValueError(
                "Synthesis provider returned no result."
            )

        answer = raw.get("answer")

        if not isinstance(answer, str):
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
    def _validate_answer_quality(
        answer: str,
        question: str,
    ) -> None:
        """Reject obvious meta/task-descriptive synthesis."""

        normalized = " ".join(
            answer.strip().lower().split()
        )

        if not normalized:
            raise ValueError(
                "Synthesis answer is empty."
            )

        meta_prefixes = (
            "the user has provided",
            "the user provided",
            "the task is to",
            "the task asks",
            "the question asks",
            "the prompt asks",
            "the supplied text",
            "the supplied material",
            "the provided text",
            "the provided information",
            "the sources provided",
            "the evidence provided",
            "based on the user's request",
        )

        if normalized.startswith(meta_prefixes):
            raise ValueError(
                "Synthesis answer is meta/task-descriptive "
                "instead of directly answering the question."
            )

        if (
            "the user has provided" in normalized
            and "answer" in normalized
        ):
            raise ValueError(
                "Synthesis answer contains a meta-response."
            )

        if not question.strip():
            raise ValueError(
                "Research question cannot be empty."
            )

    @staticmethod
    def _support_status(
        evidence_ids: tuple[str, ...],
        execution: ResearchExecutionResult,
    ) -> str:
        if not evidence_ids:
            return "insufficient"

        matched_source_ids: set[str] = set()

        for step_execution in execution.steps:
            if step_execution.result is None:
                continue

            for evidence in step_execution.result.evidence:
                if evidence.source_id in evidence_ids:
                    matched_source_ids.add(
                        evidence.source_id
                    )

        if not matched_source_ids:
            return "insufficient"

        if len(matched_source_ids) >= 2:
            return "corroborated"

        return "single_source"
