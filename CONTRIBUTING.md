# Contributing to Commenter

Thank you for your interest in contributing! Here's how to get involved.

## Development Setup

```bash
git clone https://github.com/mmeirovich/commenter.git
cd commenter
uv sync --extra dev
uv run pre-commit install
cp .env.example .env  # fill in your keys
```

## Workflow

1. **Open an issue first** for non-trivial changes — discuss before coding.
2. Fork the repo and create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes with tests.
4. Run the full check suite:
   ```bash
   uv run ruff check src/ tests/
   uv run ruff format src/ tests/
   uv run mypy src/
   uv run pytest
   ```
5. Push your branch and open a Pull Request against `main`.
6. Fill in the PR template completely.
7. Wait for CI to pass and for [@mmeirovich](https://github.com/mmeirovich) to review.

## Code Standards

- **Strict typing**: all functions must have full type annotations. `mypy --strict` must pass.
- **Ruff**: no lint errors, consistent formatting.
- **Tests**: new endpoints and agent logic need test coverage.
- **No secrets**: never commit `.env` or API keys.

## Branch Protection

The `main` branch is protected:
- Direct pushes are disabled.
- All PRs require at least **1 approval from @mmeirovich**.
- All CI status checks must pass.

## Questions?

Open a [GitHub Discussion](https://github.com/mmeirovich/commenter/discussions) or file an issue.
