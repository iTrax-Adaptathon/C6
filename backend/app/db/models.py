from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Debate(Base):
    __tablename__ = "debates_v2"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    topic: Mapped[str] = mapped_column(String(500), default="")
    side_a_text: Mapped[str] = mapped_column(Text, nullable=False)
    side_b_text: Mapped[str] = mapped_column(Text, nullable=False)
    scoring_preset: Mapped[str] = mapped_column(String(80), nullable=False)
    winner: Mapped[str] = mapped_column(String(32), nullable=False)
    full_result: Mapped[dict] = mapped_column(JSON, nullable=False)
