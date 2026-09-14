# Contributing

Keep changes focused, document any API-contract change, and do not include secrets or local environment files in a commit.

Before opening a pull request, run:

```powershell
python -m pytest backend/tests -q
```

Use a concise, imperative commit subject, such as `fix: validate compatible provider URLs`. Pull requests should explain the user-visible change and include tests when behavior changes.
