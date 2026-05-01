def validate_reliability_score(score: int) -> None:
    if score < 1 or score > 10:
        msg = "Reliability score must be between 1 and 10"
        raise ValueError(msg)


def has_minimum_quorum(active_members: int) -> bool:
    # TODO: Replace with formal electoral quorum rules.
    return active_members >= 3
