# Career Copilot API

The backend is a standalone FastAPI service for the AI Resume & Career Copilot. It provides authenticated, owner-scoped resume and job intelligence workflows backed by PostgreSQL. The recommendation and feedback services are deterministic and evidence-first: they use explicit parsers, rules, and templates rather than an LLM.

## Implemented capabilities

The API supports password-based signup and login, JWT bearer authentication, PDF/DOCX/TXT resume upload and deterministic extraction, job-description parsing, explainable resume-to-job matching, ATS-style gap notes, persisted learning roadmaps and portfolio prompts, structured interview practice feedback, private application tracking, and dashboard summaries.

All versioned routes are prefixed with `/api/v1`. Protected routes require `Authorization: Bearer <access_token>`.

| Area | Routes |
| --- | --- |
| Health | `GET /health`, `GET /health/ready` |
| Authentication | `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` |
| Account controls | `GET /account/export`, `DELETE /account` |
| Resumes | `POST /resumes/upload`, `GET /resumes`, `GET /resumes/{id}`, `PATCH /resumes/{id}` |
| Jobs | `POST /jobs`, `POST /jobs/upload`, `GET /jobs`, `GET /jobs/{id}` |
| Matching | `POST /analyses/match`, `GET /analyses/{id}` |
| Plans | `POST /plans/{analysis_id}/generate`, `GET /plans/{analysis_id}`, `PATCH /plans/items/{item_id}` |
| Interview practice | `POST /interviews`, `GET /interviews`, `GET /interviews/{id}`, `POST /interviews/{id}/responses` |
| Applications | `POST /applications`, `GET /applications`, `PATCH /applications/{id}` |
| Dashboard | `GET /dashboard` |

## Local development

Use Python 3.11 or newer. Create a virtual environment, install the dependencies, and configure a private PostgreSQL database through an untracked `.env` file.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
cp env.example .env
```

Set `DATABASE_URL` to a PostgreSQL connection string and provide a unique `JWT_SECRET` of at least 32 characters. The configuration accepts `postgresql+psycopg://`, `postgresql://`, and legacy `postgres://` URLs and normalizes them to psycopg 3. Keep credentials and uploaded files out of Git.

Apply migrations and start the service:

```bash
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

The interactive API documentation is available at `http://127.0.0.1:8001/docs`. Liveness is available at `http://127.0.0.1:8001/api/v1/health`; readiness verifies that the configured database can serve data-backed requests.

## Verification

The test suite uses isolated in-memory SQLite fixtures for fast contract and ownership checks. It does not replace PostgreSQL migration validation. Run both checks from the `backend` directory:

```bash
python -m pytest
DATABASE_URL='postgresql+psycopg://career_copilot:placeholder@localhost:5432/career_copilot' \
  python -m alembic upgrade head --sql
```

The offline migration command renders the full PostgreSQL DDL chain without connecting to a server. Before production launch, apply the same migrations to the deployment database and verify `GET /api/v1/health/ready` returns a connected state.

## Production deployment

The repository root contains `render.yaml`, which defines a Python API service and a static Next.js frontend. Configure `DATABASE_URL` as a private Render secret and allow Render to generate `JWT_SECRET`. Set `CORS_ORIGINS` to the exact HTTPS origin of the deployed frontend, without a trailing slash. Set the frontend build variable `NEXT_PUBLIC_API_BASE_URL` to the API origin ending in `/api/v1`; because Next.js inlines this value into the static bundle, changing it requires a frontend rebuild.

For container-based deployments, the root `Dockerfile.api` provides the same API runtime contract. It expects `DATABASE_URL`, `JWT_SECRET`, and `CORS_ORIGINS` at runtime and listens on `$PORT` (default `8000`). Run migrations as a release or pre-deploy command before starting multiple application instances.

The API intentionally does not expose upload paths, source file bytes, password hashes, or database connection details. Authentication attempts are throttled per client and normalized email address; the limiter is process-local and should move to a shared store before horizontal scaling. Browser clients receive a Secure, HttpOnly, SameSite cookie session; bearer responses remain temporarily available for backward compatibility with existing API consumers.
 Authenticated users can export their owner-scoped records or permanently delete their account and stored resume files. Parsed resume evidence can be user-reviewed and corrected without changing the original upload. OCR, semantic embeddings, RAG, and external LLM providers remain separate future scopes rather than simulated production features.
