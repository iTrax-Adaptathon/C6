"""Deterministic, auditable score calculation."""

from statistics import fmean

from app.schemas import ArgumentProfile, ClaimEvaluation, ClaimsBySide, LLMJudgment, ScorePair


WEIGHTS = {"logic": 0.34, "evidence": 0.33, "rebuttal": 0.33}


def _mean(claims: list[ClaimEvaluation], axis: str) -> float:
    if not claims:
        raise ValueError("Each side must contain at least one discrete claim.")
    return round(fmean(getattr(claim, f"{axis}_score") for claim in claims), 1)


def build_profile(claims: ClaimsBySide) -> ArgumentProfile:
    return ArgumentProfile(
        logic=ScorePair(a=_mean(claims.a, "logic"), b=_mean(claims.b, "logic")),
        evidence=ScorePair(a=_mean(claims.a, "evidence"), b=_mean(claims.b, "evidence")),
        rebuttal=ScorePair(a=_mean(claims.a, "rebuttal"), b=_mean(claims.b, "rebuttal")),
    )


def build_overall(profile: ArgumentProfile) -> ScorePair:
    def score(side: str) -> float:
        return round(
            profile.logic.__getattribute__(side) * WEIGHTS["logic"]
            + profile.evidence.__getattribute__(side) * WEIGHTS["evidence"]
            + profile.rebuttal.__getattribute__(side) * WEIGHTS["rebuttal"],
            1,
        )

    return ScorePair(a=score("a"), b=score("b"))


def choose_winner(overall: ScorePair, candidate_winner: str) -> str:
    """Use computed scores; model-provided winner only breaks an exact rounding tie."""
    if overall.a > overall.b:
        return "A"
    if overall.b > overall.a:
        return "B"
    return candidate_winner


def score_judgment(candidate: LLMJudgment) -> tuple[ArgumentProfile, ScorePair, str]:
    profile = build_profile(candidate.claims)
    overall = build_overall(profile)
    winner = choose_winner(overall, candidate.winner)
    return profile, overall, winner
