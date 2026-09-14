from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.schemas import ApiConfiguration, JudgmentRequest, JudgmentResponse
from app.services.judge import judge_debate
from app.services.llm_client import JudgeConfigurationError, JudgeProviderError


router = APIRouter(prefix="/api/v1", tags=["judgments"])


@router.get("/configuration", response_model=ApiConfiguration)
def get_configuration() -> ApiConfiguration:
    settings = get_settings()
    return ApiConfiguration(
        ready=bool(settings.openai_api_key),
        model=settings.openai_model,
        allow_custom_provider=settings.allow_custom_provider,
    )


@router.post("/judgments", response_model=JudgmentResponse, status_code=status.HTTP_200_OK)
def create_judgment(request: JudgmentRequest) -> JudgmentResponse:
    try:
        return judge_debate(request, get_settings())
    except JudgeConfigurationError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except JudgeProviderError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid structured analysis returned by the judge.") from error
