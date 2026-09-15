"""Coordinates model analysis and deterministic verification."""

from app.config import Settings
from app.schemas import JudgmentRequest, JudgmentResponse
from app.services.llm_client import evaluate_with_llm
from app.services.scorer import ScoringConfig, compute_score_details, run_dual_pass_evaluation


def judge_debate(request: JudgmentRequest, settings: Settings) -> JudgmentResponse:
    scoring_config = ScoringConfig(
        preset=request.scoring_preset,
        request=request,
        settings=settings,
        evaluator=evaluate_with_llm,
    )
    if settings.enable_dual_pass:
        dual_pass = run_dual_pass_evaluation(request.side_a, request.side_b, scoring_config)
        candidate = dual_pass.averaged
        profile, overall, winner, confidence, margin_of_victory, is_draw = compute_score_details(
            candidate, scoring_config, pre_penalized=True
        )
        raw_passes = [dual_pass.pass1, dual_pass.pass2]
        bias_delta = dual_pass.bias_delta
        high_variance = dual_pass.high_variance
    else:
        candidate = evaluate_with_llm(request, settings)
        profile, overall, winner, confidence, margin_of_victory, is_draw = compute_score_details(candidate, scoring_config)
        raw_passes = [candidate]
        bias_delta = {"a": 0.0, "b": 0.0}
        high_variance = False
    return JudgmentResponse(
        motion=candidate.motion,
        pull_quote=candidate.pull_quote,
        winner=winner,
        overall_score=overall,
        argument_profile=profile,
        claims=candidate.claims,
        final_verdict=candidate.final_verdict,
        verdict="Draw / Too Close to Call" if is_draw else f"Side {winner} wins",
        confidence=confidence,
        margin_of_victory=margin_of_victory,
        is_draw=is_draw,
        scoring_preset=request.scoring_preset,
        raw_passes=raw_passes,
        bias_delta=bias_delta,
        high_variance=high_variance,
    )
