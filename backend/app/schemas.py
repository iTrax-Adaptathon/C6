"""Strict API and model-output schemas."""

from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProviderSelection(StrictModel):
    mode: Literal["shared", "custom"] = "shared"
    system: Literal["openai", "compatible"] = "openai"
    api_key: str | None = Field(default=None, max_length=500)
    model: str | None = Field(default=None, max_length=120)
    base_url: str | None = Field(default=None, max_length=500)

    def valid_base_url(self) -> bool:
        if not self.base_url:
            return True
        parsed = urlparse(self.base_url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


class JudgmentRequest(StrictModel):
    topic: str = Field(default="", min_length=10, max_length=500)
    side_a: str = Field(min_length=50, max_length=20_000)
    side_b: str = Field(min_length=50, max_length=20_000)
    scoring_preset: Literal["standard_policy", "philosophical"] = "standard_policy"
    provider: ProviderSelection = Field(default_factory=ProviderSelection)

    @model_validator(mode="after")
    def validate_side_inputs(self):
        if self.side_a.strip().casefold() == self.side_b.strip().casefold():
            raise ValueError("Both sides must contain different arguments.")
        if len(self.side_a.strip()) < 50 or len(self.side_b.strip()) < 50:
            raise ValueError("Each side must contain at least 50 characters.")
        return self


class ApiConfiguration(StrictModel):
    ready: bool
    model: str
    allow_custom_provider: bool


class FallacyEvaluation(StrictModel):
    type: str = Field(min_length=1, max_length=80)
    quote: str = Field(default="", max_length=600)
    explanation: str = Field(default="", max_length=800)
    severity: Literal["minor", "moderate", "severe"] = "minor"


class ClaimEvaluation(StrictModel):
    claim: str = Field(min_length=1, max_length=600)
    logic_score: float = Field(ge=0, le=100)
    evidence_score: float = Field(ge=0, le=100)
    rebuttal_score: float = Field(ge=0, le=100)
    rhetoric_score: float = Field(ge=0, le=100, default=50.0)
    relevance_score: float = Field(ge=0, le=100, default=50.0)
    fallacies: list[FallacyEvaluation | str] = Field(default_factory=list, max_length=5)
    analysis: str = Field(min_length=1, max_length=1200)


class ScorePair(StrictModel):
    a: float = Field(ge=0, le=100)
    b: float = Field(ge=0, le=100)


class ArgumentProfile(StrictModel):
    logic: ScorePair
    evidence: ScorePair
    rebuttal: ScorePair
    rhetoric: ScorePair
    relevance: ScorePair


class ClaimsBySide(StrictModel):
    a: list[ClaimEvaluation] = Field(min_length=1, max_length=5)
    b: list[ClaimEvaluation] = Field(min_length=1, max_length=5)

    def __getitem__(self, key: str):
        return getattr(self, key)


class LLMJudgment(StrictModel):
    motion: str = Field(min_length=1, max_length=500)
    pull_quote: str = Field(min_length=1, max_length=160)
    winner: Literal["A", "B", "Draw"] = "Draw"
    claims: ClaimsBySide
    final_verdict: str = Field(min_length=40, max_length=2000)


class JudgmentResponse(StrictModel):
    motion: str
    pull_quote: str
    winner: Literal["A", "B", "Draw"]
    overall_score: ScorePair
    argument_profile: ArgumentProfile
    claims: ClaimsBySide
    final_verdict: str
    verdict: str = ""
    confidence: float = Field(ge=0, le=100)
    margin_of_victory: float = Field(ge=0, le=100)
    is_draw: bool = False
    scoring_preset: Literal["standard_policy", "philosophical"] = "standard_policy"
    raw_passes: list[LLMJudgment] = Field(default_factory=list)
    bias_delta: ScorePair = Field(default_factory=lambda: ScorePair(a=0, b=0))
    high_variance: bool = False
