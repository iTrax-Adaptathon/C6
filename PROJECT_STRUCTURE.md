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
│   │   │   ├── judge.py          # Coordinates the full judging workflow
│   │   │   ├── claim_parser.py   # Extracts claims, evidence, and assumptions
│   │   │   ├── rebuttals.py      # Maps direct replies to opposing claims
│   │   │   ├── scorer.py         # Deterministic weighted score calculation
│   │   │   └── llm_client.py     # LLM provider integration
│   │   └── prompts/
│   │       ├── extract_claims.txt
│   │       ├── evaluate_claims.txt
│   │       └── final_verdict.txt
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_scoring.py
│   ├── requirements.txt
│   └── .env.example              # Keys only; never commit a real .env file
│
└── docs/
    ├── api-contract.md           # Endpoint request/response examples
    └── scoring-rubric.md         # Definitions for logic, evidence, rebuttal
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
    → winner or justified close-call result
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

The response should include each side's component scores, claim-level explanations tied to transcript excerpts, a confidence value, limitations, and a verdict. A close or poorly supported debate must be returned as a justified close-call, not arbitrarily assigned to a side.
