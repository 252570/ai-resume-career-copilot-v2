# AI Resume & Career Copilot

[![CI](https://github.com/252570/ai-resume-career-copilot-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/252570/ai-resume-career-copilot-v2/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-informational.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)

> ⚠️ **Deterministic by design — no LLM.** Every recommendation, match score, and piece of feedback comes from explicit rules and templates over evidence in your own documents. Nothing here calls a language model or fabricates resume or job content. See the method boundary below.

AI Resume & Career Copilot is a production-oriented final-year project for building an **evidence-first career workspace**. A signed-in user can upload and parse a resume, capture a target role, inspect a deterministic and explainable comparison, turn visible gaps into a learning sequence and portfolio prompts, rehearse structured interview answers, and track applications in an owner-scoped dashboard.

> **Method boundary:** The implemented recommendation, matching, ATS-style, roadmap, project, and interview-feedback features are deterministic rules and templates. They do not call an LLM, do not fabricate resume or job evidence, and do not claim to predict a hiring outcome or judge an interview.

## Current implementation

| Area | Status | Implemented behavior |
| --- | --- | --- |
| Frontend | Complete | Next.js 15, TypeScript, Tailwind CSS, responsive owner-scoped workspace, login/signup, navigation, and workflow states. |
| API | Complete | FastAPI REST API with Pydantic contracts, request validation, controlled errors, and configured CORS. |
| Persistence | Complete | PostgreSQL-ready SQLAlchemy models and Alembic migrations `20260820_0001` through `20260822_0007`. |
| Resume evidence | Complete | Validated PDF, DOCX, and TXT upload up to 5 MB; UUID local storage; deterministic text/contact/skills/education/experience/project/certification/link extraction. |
| Job intelligence | Complete | Pasted or uploaded job descriptions with deterministic title, company, required/preferred skills, experience, education, and keyword extraction. |
| Matching and ATS-style gaps | Complete | Explainable score breakdown, matched and missing skills, source-evidence snippets, deterministic ATS coverage notes, and prioritized gaps. |
| Learning and projects | Complete | Persisted skill-gap roadmap steps and portfolio project prompts generated from the saved analysis. |
| Accounts and isolation | Complete | Bcrypt password hashing, JWT bearer tokens, owner-scoped records, and cross-account access tests. |
| Interview practice | Complete | Job-aware question sets and transparent structure feedback based on length, STAR terms, measurements, and focus-skill mention. |
| Application tracker | Complete | Private application ledger, supported status transitions, dashboard counts, and recent application summary. |
| Deferred | Deliberately deferred | OCR fallback, LLM provider abstraction, RAG assistant, semantic embeddings, resume-version editing, Docker packaging, and final deployment configuration. |

## Architecture

```text
.
├── frontend/                  # Next.js App Router client
│   ├── app/components/        # Brand mark, resume evidence panel, workspace
│   ├── app/lib/api.ts         # Public API base URL and upload boundary
│   ├── app/page.tsx           # Workspace entry page
│   └── env.example            # Public frontend environment contract
├── backend/                   # FastAPI service
│   ├── app/api/v1/            # Auth, resume, job, analysis, plans, interviews, applications, dashboard
│   ├── app/core/              # Environment configuration and safe errors
│   ├── app/db/                # SQLAlchemy base, engine, and request sessions
│   ├── app/models/            # ORM models only
│   ├── app/repositories/      # Persistence access methods
│   ├── app/schemas/           # Pydantic request and response contracts
│   ├── app/services/          # Parsers and deterministic domain services
│   ├── alembic/               # PostgreSQL migrations
│   └── tests/                 # Isolated SQLite-backed API/service tests
├── ARCHITECTURE.md
├── WINDOWS_11_POSTGRESQL_SETUP.md
└── package.json
```

The frontend remains a static Next.js export. It communicates with FastAPI through the build-time public `NEXT_PUBLIC_API_BASE_URL` value. The backend remains independently runnable on port `8001` during local development, with PostgreSQL configured only from an untracked runtime environment.

## Data model and migration chain

| Migration | Tables or changes |
| --- | --- |
| `20260820_0001` | Core `users`, `resumes`, `jobs`, `skills`, `resume_skills`, `job_skills`, and `match_results` schema. |
| `20260822_0002` | Resume extracted text and deterministic parsed-data persistence. |
| `20260822_0003` | Job parsing status and structured requirement data. |
| `20260822_0004` | `roadmap_items` and `project_recommendations` linked to an explainable match result. |
| `20260822_0005` | Password hash and active-account fields for local authentication. |
| `20260822_0006` | Owner-scoped interview sessions and response feedback. |
| `20260822_0007` | Owner-scoped job application tracking. |

## Secure local setup

Use Node.js 20+ and Python 3.11+. Install PostgreSQL locally, create a private role/database, and follow the Windows-specific walkthrough in [Windows 11 PostgreSQL Setup Guide](./WINDOWS_11_POSTGRESQL_SETUP.md) when applicable.

```bash
# 1. Install frontend dependencies at the repository root.
pnpm install

# 2. Create an untracked frontend/.env.local using frontend/env.example.
# It must contain this local API endpoint:
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001/api/v1

# 3. Create an untracked backend/.env using backend/env.example.
# Set DATABASE_URL to your own PostgreSQL credentials and set a strong JWT_SECRET.
# JWT_SECRET must be at least 32 characters; never commit it.

# 4. Install backend dependencies and apply all PostgreSQL migrations.
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head

# 5. Start FastAPI in one terminal.
python -m uvicorn app.main:app --reload --port 8001

# 6. Start the frontend in a second terminal from the project root.
pnpm dev
```

The local frontend is served at `http://localhost:3000`; FastAPI is served at `http://127.0.0.1:8001`, including `/api/v1/health` and interactive documentation at `/docs`.

## API surface

All routes below are prefixed with `/api/v1`. Protected routes require `Authorization: Bearer <access_token>`. Anonymous legacy resume/job records are supported for prior Phase 3 continuity, but new signed-in writes are bound to the bearer-token subject and cannot be retrieved by another account.

| Area | Routes | Notes |
| --- | --- | --- |
| Health | `GET /health` | No database credentials are returned. |
| Authentication | `POST /auth/signup`, `POST /auth/login`, `GET /auth/me` | Passwords are hashed with bcrypt; JWT signing uses `JWT_SECRET`. |
| Resumes | `POST /resumes/upload`, `GET /resumes`, `GET /resumes/{id}` | PDF/DOCX/TXT only; 5 MB maximum; no binary file or local path is returned. |
| Jobs | `POST /jobs`, `POST /jobs/upload`, `GET /jobs`, `GET /jobs/{id}` | Deterministically parses supplied job content. |
| Analysis | `POST /analyses/match`, `GET /analyses/{id}` | Returns score criteria, match evidence, ATS-style notes, and gaps. |
| Plans | `POST /plans/{analysis_id}/generate`, `GET /plans/{analysis_id}` | Persisted roadmap and portfolio prompts derived from saved gaps. |
| Practice | `POST /interviews`, `GET /interviews`, `GET /interviews/{id}`, `POST /interviews/{id}/responses` | Feedback contains an explicit deterministic-method disclaimer. |
| Applications | `POST /applications`, `GET /applications`, `PATCH /applications/{id}` | Supported statuses: saved, applied, screening, interviewing, offer, rejected, withdrawn. |
| Dashboard | `GET /dashboard` | Returns only the authenticated user’s counts and recent ledger entries. |

## Verification

The test suite uses isolated SQLite metadata fixtures to verify route contracts and model relationships without substituting a local PostgreSQL database. PostgreSQL migration SQL is additionally checked offline when a server is unavailable.

```bash
# Backend tests
cd backend
python -m pytest

# PostgreSQL migration SQL check; this does not connect to a server.
DATABASE_URL='postgresql+psycopg://career_copilot:placeholder@localhost:5432/career_copilot' \
  python -m alembic upgrade head --sql

# Frontend type check and static export build from repository root
cd ..
pnpm --filter career-copilot-frontend check
pnpm build
```

## Security and product boundaries

The project does not hard-code database credentials, API keys, password hashes, or JWT secrets. The browser stores only the bearer token needed for the active local session; the API never returns password hashes, upload storage paths, or source file bytes. User-owned resumes, jobs, analyses, plans, practice sessions, and application entries are checked against the authenticated account before retrieval or modification.

This repository intentionally stops before OCR, third-party AI providers, RAG, and deployment packaging. Those features require separate threat modeling, provider configuration, evaluation standards, and operational decisions rather than being represented as incomplete or simulated controls.

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Robin Kushwaha.
