from .result import ResearchResult


class ResearchValidator:

    def validate(
        self,
        result: ResearchResult,
    ) -> ResearchResult:

        if not result.question.strip():
            raise ValueError(
                "Research question is empty."
            )

        if result.sources_considered < 1:
            raise ValueError(
                "No sources were considered."
            )

        if result.sources_collected < 1:
            raise ValueError(
                "No sources were collected."
            )

        if not result.answer:
            raise ValueError(
                "Research answer is empty."
            )

        if not result.evidence:
            raise ValueError(
                "Research evidence is empty."
            )

        return result
