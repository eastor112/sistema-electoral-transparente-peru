from election_system.domain.rules import validate_reliability_score


class CalculateReliabilityUseCase:
    async def execute(self, *, mesa_id: str) -> int:
        # TODO: compute weighted factors from auditable signals.
        # Placeholder to keep architecture wiring explicit.
        score = 10
        validate_reliability_score(score=score)
        _ = mesa_id
        return score
