from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.judgments import router as judgments_router
from app.config import get_settings


settings = get_settings()
app = FastAPI(title="AI Debate Judge API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(judgments_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the existing UI and the API from one local service.
FRONTEND_DIR = Path(__file__).resolve().parents[2]
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
