from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import DateTime, Float, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


DB_PATH = Path(__file__).resolve().parent / "debates.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class DebateRecord(Base):
    __tablename__ = "debates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic: Mapped[str] = mapped_column(String(500))
    motion: Mapped[str] = mapped_column(String(500))
    winner: Mapped[str] = mapped_column(String(16))
    verdict: Mapped[str] = mapped_column(Text)
    overall_score_a: Mapped[float] = mapped_column(Float)
    overall_score_b: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    margin_of_victory: Mapped[float] = mapped_column(Float)
    is_draw: Mapped[bool] = mapped_column(default=False)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=ENGINE)


def save_debate(result: dict | object) -> None:
    record_data = result.model_dump() if hasattr(result, "model_dump") else result
    with SessionLocal() as session:
        record = DebateRecord(
            topic=record_data["motion"],
            motion=record_data["motion"],
            winner=record_data["winner"],
            verdict=record_data["final_verdict"],
            overall_score_a=record_data["overall_score"]["a"],
            overall_score_b=record_data["overall_score"]["b"],
            confidence=record_data.get("confidence", 0.0),
            margin_of_victory=record_data.get("margin_of_victory", 0.0),
            is_draw=record_data.get("is_draw", False),
            payload=str(record_data),
        )
        session.add(record)
        session.commit()


def list_debates(search: str | None = None) -> list[dict]:
    with SessionLocal() as session:
        statement = select(DebateRecord)
        if search:
            statement = statement.where(DebateRecord.topic.ilike(f"%{search}%"))
        records = session.execute(statement.order_by(DebateRecord.id.desc())).scalars().all()
        return [
            {
                "id": record.id,
                "topic": record.topic,
                "winner": record.winner,
                "overall_score": {"a": record.overall_score_a, "b": record.overall_score_b},
                "confidence": record.confidence,
                "is_draw": record.is_draw,
                "created_at": record.created_at.isoformat(),
            }
            for record in records
        ]


def get_debate(debate_id: int) -> dict | None:
    with SessionLocal() as session:
        record = session.get(DebateRecord, debate_id)
        if not record:
            return None
        return {
            "id": record.id,
            "topic": record.topic,
            "winner": record.winner,
            "overall_score": {"a": record.overall_score_a, "b": record.overall_score_b},
            "final_verdict": record.verdict,
            "confidence": record.confidence,
            "margin_of_victory": record.margin_of_victory,
            "is_draw": record.is_draw,
            "payload": record.payload,
            "created_at": record.created_at.isoformat(),
        }
