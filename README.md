# AI Resume & Career Copilot

AI Resume & Career Copilot is a production-oriented final-year project that will help users understand how their resume aligns with a target job and what practical steps can close the gap. This repository is deliberately being built in phases. **Phase 2 adds only the PostgreSQL data foundation; it does not implement resume upload/parsing, matching, AI analysis, or authentication flows.**

## Phase 2 status

| Area | Status | What exists now |
| --- | --- | --- |
| Repository architecture | Complete | Separate `frontend/`, `backend/`, documentation, environment templates, and test foundations. |
| Frontend | Complete | Next.js, TypeScript, Tailwind CSS, and a responsive phase-status landing screen. |
| Backend | Complete | FastAPI application factory, versioned health route, typed configuration boundary, and tests. |
| Database | Complete | PostgreSQL-ready SQLAlchemy models, Alembic migration, Pydantic contracts, repository boundary, and test-safe sessions. |
| Career capabilities | Deferred | Resume ingestion, job analysis, matching, ATS gaps, roadmaps, recommendations, RAG, interviews, and tracking are not yet implemented. |

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
│   │   └── main.py            # Application entry point
│   ├── alembic/               # Versioned PostgreSQL migrations
│   ├── alembic.ini
│   ├── tests/                 # Backend tests
│   ├── env.example            # Non-secret local configuration template
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

## Local development

The commands below assume Node.js 20+ and Python 3.11+.

```bash
# Frontend
cd frontend
pnpm install
pnpm dev

# Backend (in another terminal; configure PostgreSQL first)
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The frontend runs at `http://localhost:3000` by default. The backend exposes a health check at `http://localhost:8000/api/v1/health` and interactive API documentation at `http://localhost:8000/docs`.

## Verification commands

```bash
# Frontend production build and TypeScript check
pnpm build && pnpm --filter career-copilot-frontend check

# Backend tests and PostgreSQL migration SQL verification
cd backend && python3 -m pytest
DATABASE_URL='postgresql+psycopg://career_copilot:placeholder@localhost:5432/career_copilot' python3 -m alembic upgrade head --sql
```

## Scope boundary

Phase 2 provides storage metadata and normalized relationship structure only. No resume bytes are stored in the database, no document parser runs, no matching score is computed, and no LLM provider is invoked. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the phased extension plan.
