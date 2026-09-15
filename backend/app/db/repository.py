from __future__ import annotations

from sqlalchemy import or_, select

from app.db.models import Debate
from app.db.session import session_scope
from app.schemas import JudgmentRequest, JudgmentResponse


def init_db() -> None:
    from app.db.models import Base
    from app.db.session import engine

    Base.metadata.create_all(bind=engine)


def save_debate(request: JudgmentRequest, result: JudgmentResponse | dict) -> str:
    payload = result.model_dump() if hasattr(result, "model_dump") else result
    debate = Debate(
        topic=request.topic,
        side_a_text=request.side_a,
        side_b_text=request.side_b,
        scoring_preset=request.scoring_preset,
        winner=payload.get("winner", "Draw"),
        full_result=payload,
    )
    with session_scope() as session:
        session.add(debate)
        session.flush()
        return debate.id


def list_debates(page: int = 1, page_size: int = 20, query: str | None = None, winner: str | None = None) -> dict:
    page = max(1, page)
    page_size = min(100, max(1, page_size))
    with session_scope() as session:
        statement = select(Debate)
        if query:
            pattern = f"%{query}%"
            statement = statement.where(or_(Debate.topic.ilike(pattern), Debate.side_a_text.ilike(pattern), Debate.side_b_text.ilike(pattern)))
        if winner:
            statement = statement.where(Debate.winner == winner)
        records = session.execute(statement.order_by(Debate.created_at.desc())).scalars().all()
        start = (page - 1) * page_size
        items = records[start:start + page_size]
        return {
            "items": [
                {"id": item.id, "timestamp": item.created_at.isoformat(), "topic": item.topic, "winner": item.winner, "scoring_preset": item.scoring_preset}
                for item in items
            ],
            "page": page,
            "page_size": page_size,
            "total": len(records),
        }


def get_debate(debate_id: str) -> dict | None:
    with session_scope() as session:
        debate = session.get(Debate, debate_id)
        if debate is None:
            return None
        return {
            "id": debate.id,
            "timestamp": debate.created_at.isoformat(),
            "topic": debate.topic,
            "side_a_text": debate.side_a_text,
            "side_b_text": debate.side_b_text,
            "scoring_preset": debate.scoring_preset,
            "winner": debate.winner,
            "result": debate.full_result,
        }
