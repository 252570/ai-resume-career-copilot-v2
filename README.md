# AI Resume & Career Copilot

AI Resume & Career Copilot is a production-oriented final-year project that will help users understand how their resume aligns with a target job and what practical steps can close the gap. This repository is deliberately being built in phases. **Phase 1 establishes only the architecture and runnable foundations; it does not implement resume uploads, parsing, matching, user accounts, or AI features.**

## Phase 1 status

| Area | Status | What exists now |
| --- | --- | --- |
| Repository architecture | Complete | Separate `frontend/`, `backend/`, documentation, environment templates, and test foundations. |
| Frontend | Complete | Next.js, TypeScript, Tailwind CSS, and a responsive phase-status landing screen. |
| Backend | Complete | FastAPI application factory, versioned API router, typed health response, configuration boundary, and test. |
| Database | Deferred | PostgreSQL and persistent models begin in Phase 2. |
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
│   │   ├── core/              # Configuration and cross-cutting concerns
│   │   ├── schemas/           # Pydantic API contracts
│   │   └── main.py            # Application entry point
│   ├── tests/                 # Backend tests
│   ├── .env.example           # Server-only environment contract
│   └── requirements.txt
├── ARCHITECTURE.md             # Boundary decisions and future extension map
├── ideas.md                    # Chosen UI design system for the web client
└── package.json                # Convenience commands for the frontend and backend
```

## Local development

The commands below assume Node.js 20+ and Python 3.11+.

```bash
# Frontend
cd frontend
pnpm install
pnpm dev

# Backend (in another terminal)
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
cd frontend && pnpm build && pnpm check

# Backend tests
cd backend && python3 -m pytest
```

## Scope boundary

Phase 1 provides the structure required for later work. No database connection is made yet, no keys are hardcoded, no document content is stored, and no LLM provider is invoked. See [ARCHITECTURE.md](./ARCHITECTURE.md) for the phased extension plan.
