# AI Resume & Career Copilot

AI Resume & Career Copilot is a production-oriented final-year project that will help users understand how their resume aligns with a target job and what practical steps can close the gap. This repository is deliberately being built in phases. **Phase 3 adds secure resume upload and deterministic parsing only; matching, AI analysis, roadmaps, and authentication remain out of scope.**

## Phase 3 status

| Area | Status | What exists now |
| --- | --- | --- |
| Repository architecture | Complete | Separate `frontend/`, `backend/`, documentation, environment templates, and test foundations. |
| Frontend | Complete | Next.js, TypeScript, Tailwind CSS, and a responsive resume upload plus parsed-evidence interface. |
| Backend | Complete | FastAPI health, upload, and retrieval routes with strict validation, restricted CORS, and controlled errors. |
| Database | Complete | PostgreSQL-ready SQLAlchemy persistence and Alembic migrations through `20260822_0002`. |
| Resume ingestion | Complete | PDF, DOCX, and UTF-8/UTF-16 TXT upload; local development storage; deterministic text and basic signal extraction. |
| Career capabilities | Deferred | Job analysis, matching, ATS gaps, roadmaps, recommendations, RAG, interviews, tracking, and authentication. |

## Repository layout

```text
.
├── frontend/                  # Next.js 15 + TypeScript + Tailwind UI
│   ├── app/                   # App Router pages, layout, and styles
│   ├── public/                # Small static configuration assets only
│   ├── .env.example           # Public frontend environment contract
│   └── package.json
├── backend/                   # FastAPI service
│   ├── app/
│   │   ├── api/v1/            # Versioned REST route modules
│   │   ├── core/              # Configuration and safe error types
│   │   ├── db/                # SQLAlchemy base, engine, and request sessions
│   │   ├── models/            # SQLAlchemy ORM tables only
│   │   ├── repositories/      # Persistence access methods
│   │   ├── schemas/           # Pydantic API contracts only
│   │   ├── services/          # Upload storage and deterministic document parsing
│   │   └── main.py            # Application entry point
│   ├── alembic/               # Versioned PostgreSQL migrations
│   ├── storage/resumes/        # Local development uploads; contents ignored by Git
│   ├── alembic.ini
│   ├── tests/                 # Backend tests
│   ├── env.example            # Non-secret backend configuration template
│   └── requirements.txt
├── ARCHITECTURE.md             # Boundary decisions and future extension map
├── ideas.md                    # Chosen UI design system for the web client
└── package.json                # Convenience commands for the frontend and backend
```

## PostgreSQL database setup

Install PostgreSQL 15+ locally, then create a development role and database using credentials that remain on your machine. The project never stores passwords, connection strings, or deployment secrets in source control.

```bash
# Example local PostgreSQL provisioning; choose your own secure password.
createuser --pwprompt career_copilot
createdb --owner=career_copilot career_copilot

# Configure the backend from the tracked non-secret template.
cd backend
cp env.example .env
# Edit the private .env file and replace the DATABASE_URL placeholder.

# Apply the initial PostgreSQL schema.
python3 -m alembic upgrade head
```

The required `DATABASE_URL` uses the PostgreSQL Psycopg scheme below. Production values must be provided through deployment environment variables rather than a committed file.

```text
postgresql+psycopg://career_copilot:<local-password>@localhost:5432/career_copilot
```

For a step-by-step local setup on Windows, including PostgreSQL installation, role/database creation, `.env` configuration, Alembic migration, seven-table verification, and troubleshooting, see [Windows 11 PostgreSQL Setup Guide](./WINDOWS_11_POSTGRESQL_SETUP.md).

## Database models

| Model | Purpose | Key relationship or integrity rule |
| --- | --- | --- |
| `User` | Candidate profile owner. | Unique, indexed email; owns resumes and optionally saved jobs. |
| `Resume` | Resume version metadata and eventual object-storage reference. | Belongs to a user; file bytes are not stored in PostgreSQL. |
| `Job` | Captured job-description record. | May belong to a user; has required/preferred skills. |
| `Skill` | Canonical controlled vocabulary term. | Unique canonical name and reusable category. |
| `ResumeSkill` | Resume-to-skill evidence. | Composite primary key; proficiency is constrained to 1–5. |
| `JobSkill` | Job-to-skill requirement. | Composite primary key; importance is constrained to 1–5. |
| `MatchResult` | Reserved persistence contract for a future explainable analysis. | One result per resume/job/analysis version; score constrained to 0–100. |

## Phase 3 local development

The commands below assume Node.js 20+ and Python 3.11+.

```bash
# Frontend (from the project root; PowerShell-compatible)
Copy-Item frontend/env.example frontend/.env.local
# Confirm NEXT_PUBLIC_API_BASE_URL in .env.local points to http://127.0.0.1:8001/api/v1
pnpm install
pnpm.cmd dev

# Backend (in another terminal; configure PostgreSQL first)
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --port 8001
```

The frontend runs at `http://localhost:3000` by default. The backend exposes a health check at `http://127.0.0.1:8001/api/v1/health` and interactive API documentation at `http://127.0.0.1:8001/docs`.

## Resume upload API

| Route | Purpose | Constraints |
| --- | --- | --- |
| `POST /api/v1/resumes/upload` | Receives multipart field `file`, validates, stores, extracts text, parses basic signals, and persists resume metadata. | PDF, DOCX, or TXT only; maximum 5 MB; returns `201 Created`. |
| `GET /api/v1/resumes/{resume_id}` | Returns stored resume metadata and parsed evidence. | Does not return binary content or internal filesystem paths. |

The upload response includes a resume ID, original filename, detected MIME type, file size, parsing status, and only observed candidate name, email, phone, LinkedIn, GitHub, skill, education, and experience signals. Missing values remain `null` or empty lists. Uploaded source files are stored in `backend/storage/resumes/` for local development with generated UUID filenames; uploaded contents are ignored by Git and are never stored as database binary columns.

Set the frontend API boundary in a private `frontend/.env.local` file:

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001/api/v1
```

> The managed Manus preview hosts the Next.js frontend only; it does not deploy this separate Python FastAPI service. Resume uploads are therefore intentionally unavailable in the managed preview under the selected local-development-only configuration. To test upload and parsing, run the frontend at `http://localhost:3000` and FastAPI at `http://127.0.0.1:8001` on the same machine with the environment variable above.

Set backend values in a private `backend/.env` file. `DATABASE_URL` remains environment-only; `RESUME_STORAGE_DIR=storage/resumes` and `CORS_ORIGINS=http://localhost:3000` are safe local defaults.

## Verification commands

```bash
# Frontend production build and TypeScript check
pnpm build && pnpm --filter career-copilot-frontend check

# Backend tests and PostgreSQL migration SQL verification
cd backend && python3 -m pytest
DATABASE_URL='postgresql+psycopg://career_copilot:placeholder@localhost:5432/career_copilot' python3 -m alembic upgrade head --sql
```

## Scope boundary

Phase 3 persists resume metadata, extracted plain text, and deterministic parsed data only. No matching score, job analysis, ATS gap analysis, roadmap, recommendation, authentication, OCR, or LLM provider is implemented. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the phased extension plan.
