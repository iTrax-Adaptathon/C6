"""OpenAI Responses API client with schema-validated JSON output."""

import json
from pathlib import Path

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings
from app.schemas import ClaimEvaluation, ClaimsBySide, JudgmentRequest, LLMJudgment


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "evaluate_claims.txt"


class JudgeConfigurationError(RuntimeError):
    pass


class JudgeProviderError(RuntimeError):
    pass


def _schema() -> dict:
    return LLMJudgment.model_json_schema()


def _demo_judgment(request: JudgmentRequest) -> LLMJudgment:
    """Return a local, clearly labeled result when no external provider is configured."""
    def evaluate(text: str, opponent: str) -> ClaimEvaluation:
        words = max(1, len(text.split()))
        sentences = max(1, sum(text.count(mark) for mark in ".!?"))
        logic = min(88.0, 52.0 + sentences * 3.0)
        evidence = min(86.0, 48.0 + min(words, 100) * 0.25)
        rebuttal = min(84.0, 50.0 + (12.0 if opponent else 0.0))
        clarity = min(90.0, 54.0 + min(sentences, 8) * 3.0)
        relevance = 72.0 if request.topic.casefold() in text.casefold() else 62.0
        return ClaimEvaluation(
            claim=text[:600].strip(),
            logic_score=logic,
            evidence_score=evidence,
            rebuttal_score=rebuttal,
            rhetoric_score=clarity,
            relevance_score=relevance,
            fallacies=[],
            analysis="Local demo analysis: the text was scored for structure, support, response to the opposing side, clarity, and topic relevance. Configure OPENAI_API_KEY for live AI analysis.",
        )

    claim_a = evaluate(request.side_a, request.side_b)
    claim_b = evaluate(request.side_b, request.side_a)
    winner = "A" if claim_a.logic_score + claim_a.evidence_score >= claim_b.logic_score + claim_b.evidence_score else "B"
    return LLMJudgment(
        motion=request.topic,
        pull_quote="A fair judgment should explain both the strengths and weaknesses of each case.",
        winner=winner,
        claims=ClaimsBySide(a=[claim_a], b=[claim_b]),
        final_verdict=(
            f"This is a local demo analysis because no external AI key is configured. Side {winner} receives the stronger preliminary result "
            "based on the submitted structure, support, clarity, and relevance. This result is not an AI-generated fact check; configure OPENAI_API_KEY for live judging."
        ),
    )


def evaluate_with_llm(request: JudgmentRequest, settings: Settings) -> LLMJudgment:
    provider = request.provider
    if provider.mode == "custom":
        if not settings.allow_custom_provider:
            raise JudgeConfigurationError("Personal AI systems are disabled by this server administrator.")
        if not provider.api_key or not provider.model:
            raise JudgeConfigurationError("A personal API key and model are required for the selected AI system.")
        if provider.system == "compatible" and not provider.valid_base_url():
            raise JudgeConfigurationError("A valid HTTP(S) base URL is required for a compatible AI system.")
        api_key = provider.api_key
        model = provider.model
        base_url = provider.base_url if provider.system == "compatible" else None
    elif not settings.openai_api_key:
        if settings.demo_fallback:
            return _demo_judgment(request)
        raise JudgeConfigurationError("OPENAI_API_KEY is not configured. Add it to backend/.env or your environment.")
    else:
        api_key = settings.openai_api_key
        model = settings.openai_model
        base_url = None

    try:
        from openai import APIError, OpenAI
    except ImportError as error:
        raise JudgeConfigurationError(
            "The current OpenAI Python SDK is required. Run: pip install -r backend/requirements.txt"
        ) from error

    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    @retry(
        retry=retry_if_exception_type((ValueError, APIError)),
        reraise=True,
        wait=wait_exponential(multiplier=1, min=1, max=5),
        stop=stop_after_attempt(3),
    )
    def _call() -> LLMJudgment:
        response = client.responses.create(
            model=model,
            instructions=prompt,
            input=json.dumps(request.model_dump(), ensure_ascii=False),
            store=False,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "debate_judgment",
                    "strict": True,
                    "schema": _schema(),
                }
            },
        )
        try:
            return LLMJudgment.model_validate_json(response.output_text)
        except ValueError as error:
            raise ValueError("The AI judging service returned an invalid analysis.") from error

    try:
        return _call()
    except APIError as error:
        if settings.demo_fallback:
            return _demo_judgment(request)
        raise JudgeProviderError("The AI judging service is temporarily unavailable. Please try again.") from error
    except ValueError as error:
        if settings.demo_fallback:
            return _demo_judgment(request)
        raise JudgeProviderError(str(error)) from error
