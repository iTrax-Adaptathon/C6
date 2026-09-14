from app.schemas import ClaimEvaluation, LLMJudgment
from app.services.scorer import score_judgment


def claim(logic: float, evidence: float, rebuttal: float) -> ClaimEvaluation:
    return ClaimEvaluation(
        claim="A test claim.",
        logic_score=logic,
        evidence_score=evidence,
        rebuttal_score=rebuttal,
        analysis="Logic, evidence, and rebuttal were evaluated from the submitted argument.",
    )


def test_scoring_recomputes_winner_from_claims() -> None:
    judgment = LLMJudgment(
        motion="Test motion",
        pull_quote="Strong claims need support.",
        winner="B",  # Candidate can be wrong; Python must use scores.
        claims={"a": [claim(9, 8, 8)], "b": [claim(5, 5, 5)]},
        final_verdict="Side A's supported claim directly answers the weaker opposing assertion, so it wins the exchange.",
    )
    profile, overall, winner = score_judgment(judgment)

    assert profile.logic.a == 9.0
    assert overall.a > overall.b
    assert winner == "A"
