# Contributing

Thank you for improving AI Debate Judge. Keep contributions small, reviewable, and focused on one user-visible outcome.

## Before you start

- Do not commit API keys, `.env` files, virtual environments, or generated coverage files.
- Keep the deterministic scoring logic in `backend/app/services/scorer.py`.
- Update the API contract documentation when a request or response schema changes.

## Local checks

Create a virtual environment, install `backend/requirements.txt`, and run:

```powershell
python -m pytest backend/tests -q
```

Run the app manually for UI or API changes and confirm that `GET /health` responds with `{"status":"ok"}`.

## Pull requests

- Use a concise, imperative commit subject, such as `fix: validate compatible provider URLs`.
- Explain the user-facing effect and any trade-offs.
- Include tests when behavior changes.
- Keep pull requests free of unrelated formatting or generated-file changes.

GitHub Actions must pass before merging.
