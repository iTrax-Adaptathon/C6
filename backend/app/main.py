from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.debates import router as debates_router
from app.api.judgments import router as judgments_router
from app.db.repository import init_db as init_db_v2
from app.database import init_db


app = FastAPI(title="AI Debate Judge API", version="0.1.0")
app.include_router(debates_router)
app.include_router(judgments_router)
init_db()
init_db_v2()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


FRONTEND_DIR = Path(__file__).resolve().parents[2]
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
