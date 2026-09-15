from fastapi import APIRouter, HTTPException, Query

from app.db.repository import get_debate, list_debates


router = APIRouter(prefix="/api/v1/debates", tags=["debates"])


@router.get("")
def history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, max_length=200),
    winner: str | None = Query(default=None, max_length=32),
) -> dict:
    return list_debates(page=page, page_size=page_size, query=q, winner=winner)


@router.get("/{debate_id}")
def history_detail(debate_id: str) -> dict:
    result = get_debate(debate_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Debate not found.")
    return result
