"""Deterministic, auditable score calculation with bias mitigation."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import fmean
from typing import Callable

from app.schemas import (
    ArgumentProfile,
    ClaimEvaluation,
    ClaimsBySide,
    FallacyEvaluation,
    JudgmentRequest,
    LLMJudgment,
    ScorePair,
)

PRESETS = {
    "standard_policy": {"logic": 0.30, "evidence": 0.30, "rebuttal": 0.20, "rhetoric": 0.10, "relevance": 0.10},
    "philosophical": {"logic": 0.35, "evidence": 0.15, "rebuttal": 0.20, "rhetoric": 0.20, "relevance": 0.10},
}

SEVERITY_PENALTIES = {"minor": 2.0, "moderate": 5.0, "severe": 10.0}
LOGIC_FALLACIES = {
    "ad_hominem", "straw_man", "slippery_slope", "false_dilemma", "hasty_generalization", "circular_reasoning",
}
RELEVANCE_FALLACIES = {"red_herring", "appeal_to_emotion"}


@dataclass
class ScoringConfig:
    preset: str = "standard_policy"
    request: JudgmentRequest | None = None
    settings: object | None = None
    evaluator: Callable[[JudgmentRequest, object], LLMJudgment] | None = None
    weights: dict[str, float] = field(init=False)

    def __post_init__(self) -> None:
        if self.preset not in PRESETS:
            raise ValueError(f"Unknown scoring preset: {self.preset}")
        self.weights = PRESETS[self.preset].copy()


@dataclass
class DualPassResult:
    pass1: LLMJudgment
    pass2: LLMJudgment
    averaged: LLMJudgment
    bias_delta: ScorePair
    high_variance: bool


def _coerce_claims(claims: ClaimsBySide | dict) -> ClaimsBySide:
    if isinstance(claims, ClaimsBySide):
        return claims
    if isinstance(claims, dict):
        return ClaimsBySide.model_validate(claims)
    raise TypeError("claims must be a ClaimsBySide instance or a dict")


def _weighted_average(a: float, b: float) -> float:
    return round((a + b) / 2, 1)


def _fallacy_parts(fallacy: FallacyEvaluation | str | dict) -> tuple[str, str]:
    if isinstance(fallacy, dict):
        fallacy = FallacyEvaluation.model_validate(fallacy)
    if isinstance(fallacy, str):
        normalized = fallacy.strip().lower().replace(" ", "_")
        legacy_map = {
            "ad_hominem": "ad_hominem", "straw_man": "straw_man", "slippery_slope": "slippery_slope",
            "false_dilemma": "false_dilemma", "red_herring": "red_herring",
            "appeal_to_emotion": "appeal_to_emotion", "circular_reasoning": "circular_reasoning",
            "unsupported_assertion": "unsupported_assertion",
        }
        return legacy_map.get(normalized, normalized), "moderate"
    return fallacy.type.strip().lower().replace(" ", "_"), fallacy.severity


def apply_fallacy_penalties(scores: dict[str, float], fallacies: list[FallacyEvaluation | str | dict]) -> dict[str, float]:
    """Deduct severity-weighted penalties from the affected scoring dimensions."""
    adjusted = scores.copy()
    for fallacy in fallacies:
        fallacy_type, severity = _fallacy_parts(fallacy)
        penalty = SEVERITY_PENALTIES[severity]
        if fallacy_type in LOGIC_FALLACIES:
            adjusted["logic"] = max(0.0, adjusted["logic"] - penalty)
        elif fallacy_type in RELEVANCE_FALLACIES:
            adjusted["relevance"] = max(0.0, adjusted["relevance"] - penalty)
    return adjusted


def _apply_fallacy_penalties_to_claims(claims: ClaimsBySide) -> ClaimsBySide:
    def adjust(items: list[ClaimEvaluation]) -> list[ClaimEvaluation]:
        result = []
        for claim in items:
            scores = apply_fallacy_penalties(
                {"logic": claim.logic_score, "evidence": claim.evidence_score, "rebuttal": claim.rebuttal_score,
                 "rhetoric": claim.rhetoric_score, "relevance": claim.relevance_score},
                claim.fallacies,
            )
            result.append(claim.model_copy(update={**{f"{key}_score": value for key, value in scores.items()}}))
        return result
    return ClaimsBySide(a=adjust(claims.a), b=adjust(claims.b))


def _mean(claims: list[ClaimEvaluation], axis: str) -> float:
    if not claims:
        raise ValueError("Each side must contain at least one discrete claim.")
    return round(fmean(getattr(claim, f"{axis}_score") for claim in claims), 1)


def normalize_dual_pass_scores(claims: ClaimsBySide | dict) -> ClaimsBySide:
    """Average corresponding scores from two already-comparable sides."""
    claims = _coerce_claims(claims)
    count = max(len(claims.a), len(claims.b))
    normalized_a: list[ClaimEvaluation] = []
    normalized_b: list[ClaimEvaluation] = []
    for index in range(count):
        a_claim = claims.a[index] if index < len(claims.a) else claims.a[-1]
        b_claim = claims.b[index] if index < len(claims.b) else claims.b[-1]
        normalized_a.append(a_claim.model_copy(update={
            "logic_score": _weighted_average(a_claim.logic_score, b_claim.logic_score),
            "evidence_score": _weighted_average(a_claim.evidence_score, b_claim.evidence_score),
            "rebuttal_score": _weighted_average(a_claim.rebuttal_score, b_claim.rebuttal_score),
            "rhetoric_score": _weighted_average(a_claim.rhetoric_score, b_claim.rhetoric_score),
            "relevance_score": _weighted_average(a_claim.relevance_score, b_claim.relevance_score),
        }))
        normalized_b.append(b_claim.model_copy(update={
            "logic_score": _weighted_average(b_claim.logic_score, a_claim.logic_score),
            "evidence_score": _weighted_average(b_claim.evidence_score, a_claim.evidence_score),
            "rebuttal_score": _weighted_average(b_claim.rebuttal_score, a_claim.rebuttal_score),
            "rhetoric_score": _weighted_average(b_claim.rhetoric_score, a_claim.rhetoric_score),
            "relevance_score": _weighted_average(b_claim.relevance_score, a_claim.relevance_score),
        }))
    return ClaimsBySide(a=normalized_a, b=normalized_b)


def build_profile(claims: ClaimsBySide | dict) -> ArgumentProfile:
    claims = _coerce_claims(claims)
    return ArgumentProfile(
        logic=ScorePair(a=_mean(claims.a, "logic"), b=_mean(claims.b, "logic")),
        evidence=ScorePair(a=_mean(claims.a, "evidence"), b=_mean(claims.b, "evidence")),
        rebuttal=ScorePair(a=_mean(claims.a, "rebuttal"), b=_mean(claims.b, "rebuttal")),
        rhetoric=ScorePair(a=_mean(claims.a, "rhetoric"), b=_mean(claims.b, "rhetoric")),
        relevance=ScorePair(a=_mean(claims.a, "relevance"), b=_mean(claims.b, "relevance")),
    )


def build_overall(
    profile: ArgumentProfile,
    fallacy_penalty_a: float = 0.0,
    fallacy_penalty_b: float = 0.0,
    config: ScoringConfig | None = None,
) -> ScorePair:
    weights = (config or ScoringConfig()).weights

    def score(side: str) -> float:
        penalty = fallacy_penalty_a if side == "a" else fallacy_penalty_b
        value = (
            profile.logic.__getattribute__(side) * weights["logic"]
            + profile.evidence.__getattribute__(side) * weights["evidence"]
            + profile.rebuttal.__getattribute__(side) * weights["rebuttal"]
            + profile.rhetoric.__getattribute__(side) * weights["rhetoric"]
            + profile.relevance.__getattribute__(side) * weights["relevance"]
            - penalty
        )
        return round(max(0.0, min(100.0, value)), 1)

    return ScorePair(a=score("a"), b=score("b"))


def _total(profile: ArgumentProfile, side: str, config: ScoringConfig) -> float:
    return round(sum(getattr(profile, axis).__getattribute__(side) * weight for axis, weight in config.weights.items()), 1)


def compute_confidence(
    side_a_total: float,
    side_b_total: float,
    pass1_a: float,
    pass1_b: float,
    pass2_a: float,
    pass2_b: float,
) -> float:
    variance = (abs(pass1_a - pass2_a) + abs(pass1_b - pass2_b)) / 2
    return round(max(0.0, min(100.0, 100.0 - variance * 5)), 1)


def _average_judgments(pass1: LLMJudgment, pass2_swapped: LLMJudgment) -> LLMJudgment:
    remapped = ClaimsBySide(a=pass2_swapped.claims.b, b=pass2_swapped.claims.a)
    averaged_claims = normalize_dual_pass_scores(ClaimsBySide(a=pass1.claims.a, b=remapped.a))
    averaged_b = normalize_dual_pass_scores(ClaimsBySide(a=pass1.claims.b, b=remapped.b))
    claims = ClaimsBySide(a=averaged_claims.a, b=averaged_b.a)
    return pass1.model_copy(update={"claims": claims})


def run_dual_pass_evaluation(side_a: str, side_b: str, config: ScoringConfig) -> DualPassResult:
    """Evaluate both label orders and average the remapped, penalized results."""
    if config.request is None or config.evaluator is None or config.settings is None:
        raise ValueError("ScoringConfig requires request, settings, and evaluator for dual-pass evaluation")
    request = config.request
    evaluate = config.evaluator
    pass1_request = request.model_copy(update={"side_a": side_a, "side_b": side_b})
    pass2_request = request.model_copy(update={"side_a": side_b, "side_b": side_a})
    pass1 = evaluate(pass1_request, config.settings)
    pass2 = evaluate(pass2_request, config.settings)
    pass1 = pass1.model_copy(update={"claims": _apply_fallacy_penalties_to_claims(pass1.claims)})
    pass2 = pass2.model_copy(update={"claims": _apply_fallacy_penalties_to_claims(pass2.claims)})
    averaged = _average_judgments(pass1, pass2)
    config_for_profile = config
    profile1 = build_profile(pass1.claims)
    profile2 = build_profile(ClaimsBySide(a=pass2.claims.b, b=pass2.claims.a))
    totals1 = ScorePair(a=_total(profile1, "a", config_for_profile), b=_total(profile1, "b", config_for_profile))
    totals2 = ScorePair(a=_total(profile2, "a", config_for_profile), b=_total(profile2, "b", config_for_profile))
    bias_delta = ScorePair(a=round(abs(totals1.a - totals2.a), 1), b=round(abs(totals1.b - totals2.b), 1))
    return DualPassResult(pass1=pass1, pass2=pass2, averaged=averaged, bias_delta=bias_delta, high_variance=max(bias_delta.a, bias_delta.b) > 10)


def choose_winner(overall: ScorePair, candidate_winner: str) -> str:
    score_gap = abs(overall.a - overall.b)
    if score_gap < 1.0:
        return "Draw"
    if overall.a > overall.b:
        return "A"
    if overall.b > overall.a:
        return "B"
    return candidate_winner if candidate_winner in {"A", "B"} else "Draw"


def compute_score_details(
    candidate: LLMJudgment,
    config: ScoringConfig | None = None,
    pre_penalized: bool = False,
) -> tuple[ArgumentProfile, ScorePair, str, float, float, bool]:
    scoring_config = config or ScoringConfig()
    normalized_claims = candidate.claims if pre_penalized else _apply_fallacy_penalties_to_claims(candidate.claims)
    profile = build_profile(normalized_claims)
    overall = build_overall(profile, config=scoring_config)
    winner = choose_winner(overall, candidate.winner)
    margin_of_victory = round(abs(overall.a - overall.b), 1)
    confidence = round(max(0.0, min(100.0, 100.0 - margin_of_victory)), 1)
    is_draw = winner == "Draw"
    return profile, overall, winner, confidence, margin_of_victory, is_draw


def score_judgment(candidate: LLMJudgment) -> tuple[ArgumentProfile, ScorePair, str]:
    profile, overall, winner, _, _, _ = compute_score_details(candidate)
    return profile, overall, winner
