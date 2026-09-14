"""Coordinates model analysis and deterministic verification."""

from app.config import Settings
from app.schemas import JudgmentRequest, JudgmentResponse
from app.services.llm_client import evaluate_with_llm
from app.services.scorer import score_judgment


def judge_debate(request: JudgmentRequest, settings: Settings) -> JudgmentResponse:
    candidate = evaluate_with_llm(request, settings)
    profile, overall, winner = score_judgment(candidate)
    return JudgmentResponse(
        motion=candidate.motion,
        pull_quote=candidate.pull_quote,
        winner=winner,
        overall_score=overall,
        argument_profile=profile,
        claims=candidate.claims,
        final_verdict=candidate.final_verdict,
    )
