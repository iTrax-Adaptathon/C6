# AI Debate Judge — Project Structure

This document is the shared reference for the project layout. The current UI remains in the repository root; Python services belong in `backend/`.

```text
C6/
├── index.html                    # Existing browser entry point
├── styles.css                    # Existing UI styles
├── script.js                     # Existing UI behaviour; will call the API
├── README.md                     # Project overview and local setup
├── PROJECT_STRUCTURE.md          # This shared structure reference
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application and route registration
│   │   ├── config.py             # Environment/configuration settings
│   │   ├── schemas.py            # Request and response Pydantic models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── judgments.py      # POST /api/v1/judgments endpoint
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── judge.py          # Coordinates judging and consistency checks
│   │   │   ├── scorer.py         # Deterministic weighted score calculation
│   │   │   └── llm_client.py     # LLM provider integration
│   │   └── prompts/
│   │       └── evaluate_claims.txt
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_scoring.py
│   ├── requirements.txt
│   └── .env.example              # Keys only; never commit a real .env file
│
└── .gitignore                    # Local secrets and Python artifacts
```

## Ownership boundaries

| Area | Responsibility |
| --- | --- |
| `index.html`, `styles.css`, `script.js` | Frontend input, loading states, and result rendering |
| `backend/app/api/` | HTTP validation, status codes, and API responses |
| `backend/app/services/` | Claim analysis, rebuttal comparison, scoring, and verdict generation |
| `backend/app/prompts/` | Versioned LLM prompts with structured-output instructions |
| `backend/tests/` | API and scoring regression coverage |
| `docs/` | Team-facing contracts and judging rules |

## Required judgment flow

```text
Transcript input
    → claim/evidence extraction
    → cross-side rebuttal mapping
    → logic, evidence, and rebuttal assessment
    → deterministic weighted score calculation
    → deterministic winner and justified verdict
    → structured API response for the UI
```

The score calculation should stay in `services/scorer.py`, rather than being left entirely to an LLM. This makes the outcome repeatable and lets the team explain why one side won.

## Initial API contract

`POST /api/v1/judgments`

```json
{
  "topic": "Should cities restrict private cars downtown?",
  "side_a": "Argument for the motion...",
  "side_b": "Argument against the motion..."
}
```

The response includes each side's component scores, claim-level explanations, and a verdict. If scores are close, the verdict must identify the decisive claim exchange rather than rely on rhetoric or a coin flip.
