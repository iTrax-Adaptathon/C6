"""Strict API and model-output schemas."""

from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field


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
    topic: str = Field(default="", max_length=500)
    side_a: str = Field(min_length=20, max_length=20_000)
    side_b: str = Field(min_length=20, max_length=20_000)
    provider: ProviderSelection = Field(default_factory=ProviderSelection)


class ApiConfiguration(StrictModel):
    ready: bool
    model: str
    allow_custom_provider: bool


class ClaimEvaluation(StrictModel):
    claim: str = Field(min_length=1, max_length=600)
    logic_score: float = Field(ge=0, le=10)
    evidence_score: float = Field(ge=0, le=10)
    rebuttal_score: float = Field(ge=0, le=10)
    analysis: str = Field(min_length=1, max_length=1_200)


class ScorePair(StrictModel):
    a: float = Field(ge=0, le=10)
    b: float = Field(ge=0, le=10)


class ArgumentProfile(StrictModel):
    logic: ScorePair
    evidence: ScorePair
    rebuttal: ScorePair


class ClaimsBySide(StrictModel):
    a: list[ClaimEvaluation] = Field(min_length=1, max_length=5)
    b: list[ClaimEvaluation] = Field(min_length=1, max_length=5)


class LLMJudgment(StrictModel):
    """The candidate analysis returned by the model before Python verifies it."""

    motion: str = Field(min_length=1, max_length=500)
    pull_quote: str = Field(min_length=1, max_length=160)
    winner: Literal["A", "B"]
    claims: ClaimsBySide
    final_verdict: str = Field(min_length=40, max_length=2_000)


class JudgmentResponse(StrictModel):
    motion: str
    pull_quote: str
    winner: Literal["A", "B"]
    overall_score: ScorePair
    argument_profile: ArgumentProfile
    claims: ClaimsBySide
    final_verdict: str
