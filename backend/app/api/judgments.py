from fastapi import APIRouter, HTTPException, Query, status

from app.config import get_settings
from app.db.repository import save_debate as save_debate_v2
from app.database import get_debate, list_debates, save_debate
from app.schemas import ApiConfiguration, JudgmentRequest, JudgmentResponse
from app.services import judge as judge_service
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
        result = judge_service.judge_debate(request, get_settings())
        save_debate_v2(request, result)
        return result
    except JudgeConfigurationError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except JudgeProviderError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error


@router.get("/debates")
def list_history(search: str | None = Query(default=None)) -> list[dict]:
    return list_debates(search=search)


@router.get("/debates/{debate_id}")
def get_history_item(debate_id: int) -> dict:
    item = get_debate(debate_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debate not found.")
    return item
