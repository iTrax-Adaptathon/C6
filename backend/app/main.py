from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.judgments import router as judgments_router


app = FastAPI(title="AI Debate Judge API", version="0.1.0")
app.include_router(judgments_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the existing UI and the API from one local service.
FRONTEND_DIR = Path(__file__).resolve().parents[2]
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
