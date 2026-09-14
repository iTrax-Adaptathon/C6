"""OpenAI Responses API client with schema-validated JSON output."""

import json
from pathlib import Path

from app.config import Settings
from app.schemas import JudgmentRequest, LLMJudgment


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "evaluate_claims.txt"


class JudgeConfigurationError(RuntimeError):
    pass


class JudgeProviderError(RuntimeError):
    pass


def _schema() -> dict:
    return LLMJudgment.model_json_schema()


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
        raise JudgeConfigurationError(
            "OPENAI_API_KEY is not configured. Add it to backend/.env or your environment."
        )
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
    try:
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
        return LLMJudgment.model_validate_json(response.output_text)
    except APIError as error:
        raise JudgeProviderError("The AI judging service is temporarily unavailable. Please try again.") from error
    except ValueError as error:
        raise JudgeProviderError("The AI judging service returned an invalid analysis. Please try again.") from error
