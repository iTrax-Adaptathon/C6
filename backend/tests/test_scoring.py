from app.schemas import ClaimEvaluation, LLMJudgment
from app.services.scorer import (
    ScoringConfig,
    apply_fallacy_penalties,
    compute_confidence,
    normalize_dual_pass_scores,
    run_dual_pass_evaluation,
    score_judgment,
)


def claim(
    logic: float,
    evidence: float,
    rebuttal: float,
    rhetoric: float = 7.0,
    relevance: float = 7.0,
    fallacies: list[str] | None = None,
) -> ClaimEvaluation:
    return ClaimEvaluation(
        claim="A test claim.",
        logic_score=logic,
        evidence_score=evidence,
        rebuttal_score=rebuttal,
        rhetoric_score=rhetoric,
        relevance_score=relevance,
        fallacies=fallacies or [],
        analysis="Logic, evidence, and rebuttal were evaluated from the submitted argument.",
    )


def test_scoring_recomputes_winner_from_claims() -> None:
    judgment = LLMJudgment(
        motion="Test motion",
        pull_quote="Strong claims need support.",
        winner="B",
        claims={"a": [claim(9, 8, 8)], "b": [claim(5, 5, 5)]},
        final_verdict="Side A's supported claim directly answers the weaker opposing assertion, so it wins the exchange.",
    )
    profile, overall, winner = score_judgment(judgment)

    assert profile.logic.a == 9.0
    assert overall.a > overall.b
    assert winner == "A"


def test_close_scores_produce_draw() -> None:
    judgment = LLMJudgment(
        motion="Close call",
        pull_quote="Small advantages matter in close cases.",
        winner="A",
        claims={"a": [claim(7.5, 7.4, 7.2)], "b": [claim(7.3, 7.2, 7.1)]},
        final_verdict="The difference is too small for a confident conclusion.",
    )
    _, overall, winner = score_judgment(judgment)
    assert abs(overall.a - overall.b) < 0.3
    assert winner == "Draw"


def test_fallacy_penalty_reduces_score() -> None:
    judgment = LLMJudgment(
        motion="Fallacy test",
        pull_quote="Claims should be evaluated by evidence and reasoning.",
        winner="B",
        claims={
            "a": [claim(8, 7, 7, fallacies=["Ad Hominem", "False Dilemma"])],
            "b": [claim(7, 8, 8, fallacies=[])]
        },
        final_verdict="The better-supported side wins because the other side relied on fallacious reasoning.",
    )
    _, overall, _ = score_judgment(judgment)
    assert overall.a < 8.0
    assert overall.a < overall.b


def test_dual_pass_normalization_reduces_position_bias() -> None:
    a_claims = [claim(8, 8, 8, rhetoric=8, relevance=8)]
    b_claims = [claim(8, 8, 8, rhetoric=8, relevance=8)]

    normalized = normalize_dual_pass_scores({"a": a_claims, "b": b_claims})
    assert normalized["a"][0].logic_score == 8.0
    assert normalized["b"][0].logic_score == 8.0


def test_fallacy_penalties_use_severity_and_clamp_dimensions() -> None:
    adjusted = apply_fallacy_penalties(
        {"logic": 4.0, "relevance": 4.0},
        [{"type": "ad_hominem", "severity": "severe"}, {"type": "red_herring", "severity": "moderate"}],
    )
    assert adjusted["logic"] == 0.0
    assert adjusted["relevance"] == 0.0


def test_confidence_decreases_with_pass_disagreement() -> None:
    assert compute_confidence(70, 60, 70, 60, 70, 60) == 100.0
    assert compute_confidence(70, 60, 70, 60, 50, 80) == 0.0


def test_dual_pass_remaps_and_averages_scores() -> None:
    request = {
        "topic": "A sufficiently descriptive debate topic",
        "side_a": "A" * 60,
        "side_b": "B" * 60,
    }
    from app.schemas import JudgmentRequest

    first = LLMJudgment(
        motion="Test motion", pull_quote="Evidence matters.", winner="A",
        claims={"a": [claim(80, 80, 80)], "b": [claim(40, 40, 40)]},
        final_verdict="Side A has the stronger exchange because its reasoning is better supported.",
    )
    second = LLMJudgment(
        motion="Test motion", pull_quote="Evidence matters.", winner="B",
        claims={"a": [claim(70, 70, 70)], "b": [claim(50, 50, 50)]},
        final_verdict="Side B has the stronger exchange because its reasoning is better supported.",
    )
    passes = iter([first, second])
    result = run_dual_pass_evaluation(
        request["side_a"], request["side_b"],
        ScoringConfig(request=JudgmentRequest(**request), settings=object(), evaluator=lambda *_: next(passes)),
    )
    assert result.averaged.claims.a[0].logic_score == 65.0
    assert result.averaged.claims.b[0].logic_score == 55.0
    assert result.bias_delta.a == 24.0
    assert result.high_variance is True
