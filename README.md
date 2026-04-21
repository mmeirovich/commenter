# Commenter API

[![CI](https://github.com/mmeirovich/commenter/actions/workflows/ci.yml/badge.svg)](https://github.com/mmeirovich/commenter/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**An AI-powered REST API that generates thoughtful, opinionated blog post comments using a multi-agent [CrewAI](https://crewai.com/) pipeline.**

Given a post title and body, the API runs a four-agent crew that analyzes the content, researches supporting or contrarian data, forms a clear opinion, and writes a concise, engaging comment — optionally citing a relevant source.

---

## Architecture

```
POST /comment/
     │
     ▼
┌─────────────────────────────────────────────────┐
│                 CrewAI Pipeline                  │
│                                                 │
│  1. Post Analyst   ──▶  2. Web Researcher       │
│     (reads post)           (Serper web search)  │
│         │                       │               │
│         └──────────┬────────────┘               │
│                    ▼                            │
│           3. Opinion Strategist                 │
│              (forms a stance)                   │
│                    │                            │
│                    ▼                            │
│           4. Comment Writer                     │
│              (final output)                     │
└─────────────────────────────────────────────────┘
```

### Agents

| Agent | Role |
|---|---|
| **Post Analyst** | Extracts thesis, key claims, strengths, and gaps |
| **Web Researcher** | Searches for recent data and contrarian viewpoints via Serper |
| **Opinion Strategist** | Decides on a clear, evidence-backed stance |
| **Comment Writer** | Writes the final comment (3–6 sentences, with optional URL) |

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check — returns `{"status": "ok", "version": "..."}` |
| `POST` | `/comment/` | Generate a comment for a blog post |
| `GET` | `/docs` | Interactive Swagger UI |
| `GET` | `/redoc` | ReDoc API documentation |

---

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- An [OpenAI API key](https://platform.openai.com/)
- A [Serper.dev API key](https://serper.dev/) (free tier available — used for web search)

### Setup

```bash
git clone https://github.com/mmeirovich/commenter.git
cd commenter

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env and fill in OPENAI_API_KEY and SERPER_API_KEY

# Run the server
uv run commenter
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

### Development mode (auto-reload)

```bash
DEBUG=true uv run commenter
```

### Run with Docker

```bash
docker build -t commenter .
docker run --rm \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e SERPER_API_KEY=... \
  commenter
```

---

## Usage

### Health Check

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "version": "0.1.0"}
```

### Generate a Comment

```bash
curl -X POST http://localhost:8000/comment/ \
  -H "Content-Type: application/json" \
  -d '{
    "post_title": "Why Python is Still King in 2026",
    "post_text": "Python continues to dominate the AI and data science landscape. Despite challenges from Julia and Rust, Python'\''s ecosystem remains unmatched..."
  }'
```

```json
{
  "comment": "Python'\''s dominance isn'\''t just ecosystem inertia — it'\''s the deliberate bet of the ML community. The real question is whether Rust-backed tools like PyO3 and uv signal a hybrid future where Python stays the glue but cedes the hot paths. Worth noting that TIOBE'\''s April 2026 index still shows Python widening its lead, not shrinking it. What does your data say about Julia adoption in production ML workloads?",
  "summary": "Agrees with Python'\''s dominance but questions whether a Rust-hybrid model is the actual long-term trajectory.",
  "sources": ["https://www.tiobe.com/tiobe-index/"]
}
```

---

## Development

### Install dev dependencies

```bash
uv sync --extra dev
```

### Run tests

```bash
uv run pytest
```

### Lint & format

```bash
uv run ruff check src/ tests/     # lint
uv run ruff format src/ tests/    # format
uv run mypy src/                  # type check
```

### Pre-commit hooks

```bash
uv run pre-commit install
```

---

## Configuration

All configuration is via environment variables (or a `.env` file):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | _(required)_ | OpenAI API key |
| `SERPER_API_KEY` | _(required)_ | Serper.dev key for web search |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used by all agents |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Bind port |
| `DEBUG` | `false` | Enable uvicorn auto-reload |
| `LOG_LEVEL` | `INFO` | Log verbosity |

### Sync local `.env` to GitHub Secrets

Use the helper script whenever you want to push your local `.env` values into repository secrets for CI/CD:

```bash
uv run python scripts/sync_env_to_github_secrets.py
```

Optional flags:

- `--dry-run` prints the secret names that would be uploaded
- `--repo owner/repo` targets a different repository
- `--exclude NAME` skips a specific variable

The script uploads every key in `.env` as a GitHub Actions secret with the same name. It requires `gh auth login` first.

### Cloud Run deployment from GitHub Actions

The CI workflow will deploy on every push to `main` and on manual `workflow_dispatch`.

Expected GitHub repository secrets:

| Secret | Purpose |
|---|---|
| `GCP_SA_KEY` | Minified Google Cloud service account JSON for deployment auth |
| `OPENAI_API_KEY` | Runtime app config |
| `SERPER_API_KEY` | Runtime app config |
| `OPENAI_MODEL` | Runtime app config |
| `HOST` | Runtime app config |
| `PORT` | Runtime app config and Cloud Run container port |
| `DEBUG` | Runtime app config |
| `LOG_LEVEL` | Runtime app config |

Cloud Run target:

- Project: `gen-lang-client-0727840060`
- Region: `europe-west1`
- Service: `commenter`

---

## Project Structure

```
commenter/
├── src/
│   └── commenter/
│       ├── agents/
│       │   └── crew.py          # CrewAI agent definitions & pipeline
│       ├── core/
│       │   └── config.py        # Pydantic Settings
│       ├── models/
│       │   ├── comment.py       # Request / response schemas
│       │   └── health.py        # Health response schema
│       ├── routers/
│       │   ├── comment.py       # POST /comment/ endpoint
│       │   └── health.py        # GET /health endpoint
│       └── main.py              # FastAPI app factory + entrypoint
├── tests/
│   ├── test_comment.py
│   └── test_health.py
├── .github/
│   ├── workflows/ci.yml         # GitHub Actions CI
│   ├── CODEOWNERS               # Requires review from @mmeirovich
│   └── PULL_REQUEST_TEMPLATE.md
├── .env.example
├── .pre-commit-config.yaml
└── pyproject.toml
```

---

## Contributing

Contributions are welcome! Please read the guidelines below before opening a PR.

1. **Fork** the repository and create your branch from `main`.
2. **Write tests** for any new functionality.
3. **Ensure CI passes**: lint, type check, and tests must all be green.
4. **Open a Pull Request** — all PRs require review and approval from [@mmeirovich](https://github.com/mmeirovich) before merging.
5. **One approval required** — this is enforced via branch protection rules.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## License

[MIT](LICENSE)
