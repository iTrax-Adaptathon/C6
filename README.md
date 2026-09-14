# C6 — AI Debate Judge

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for the shared frontend/backend layout and implementation boundaries.

## Run the backend

1. Create and activate a Python 3.11+ virtual environment: `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1`
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY` in your environment.
4. From `backend/`, run: `uvicorn app.main:app --reload --port 8000`

Open `http://127.0.0.1:8000` in a browser. The same service provides the UI and API; check the API with `GET /health`.

## AI-system selection

The UI defaults to the backend's shared AI judge. In `backend/.env`, set `ALLOW_CUSTOM_PROVIDER=true` to allow users to select their own OpenAI API or an OpenAI-compatible Responses API endpoint. Personal credentials are used for that request only and are not saved by the application.
