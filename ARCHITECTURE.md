# Architecture — Phase 1 Foundation

## Intent

The project is organized as a modular, independently runnable web client and REST API. This prevents document processing, persistence, and AI orchestration from leaking into the presentation layer as the platform grows.

```text
┌─────────────────────────────────────────────────────────┐
│ Next.js frontend                                          │
│ app/ · components/ · typed HTTP client (Phase 3 onward)  │
└────────────────────────────┬────────────────────────────┘
                             │ HTTPS / JSON
┌────────────────────────────▼────────────────────────────┐
│ FastAPI backend                                           │
│ api/v1/ → service layer → repositories → SQLAlchemy      │
└────────────────────────────┬────────────────────────────┘
                             │ Phase 2 onward
┌────────────────────────────▼────────────────────────────┐
│ PostgreSQL                                                 │
│ users · resumes · analyses · roadmaps · applications      │
└─────────────────────────────────────────────────────────┘
```

## Current modules

| Module | Responsibility in Phase 1 | Future extension boundary |
| --- | --- | --- |
| `frontend/app` | Present the responsive product shell and Phase 1 state. | Dashboard, upload flows, result visualizations, authenticated routes. |
| `backend/app/api/v1` | Expose versioned HTTP routing and service health. | Resume, jobs, analyses, roadmaps, recommendations, interviews, applications. |
| `backend/app/schemas` | Define serializable request/response models. | Resource contracts and explainability payloads. |
| `backend/app/core` | Centralize validated server configuration. | Logging, security settings, database factory, provider configuration. |
| `backend/tests` | Verify the public service contract. | Unit, integration, authorization, and security tests. |

## API conventions

All future REST routes will live under `/api/v1`. Request bodies and responses will use Pydantic models. A typical feature will be structured as follows:

```text
api/v1/resumes.py          # HTTP concerns: request validation and status codes
services/resume_service.py # Use-case orchestration
repositories/resume_repository.py # SQLAlchemy persistence
schemas/resume.py          # Explicit external data contracts
```

The application will return meaningful HTTP status codes and problem-oriented error bodies. API keys and connection strings are loaded only through environment variables; `.env` files are ignored by Git.

## Deferred implementation map

| Phase | Planned addition | Architecture impact |
| ---: | --- | --- |
| 2 | PostgreSQL and Alembic migrations | Add database session factory, SQLAlchemy models, repository tests. |
| 3–4 | Resume upload, parsing, intelligence | Add private file storage abstraction, parser adapters, normalized resume schemas. |
| 5–7 | Job analysis, matching, ATS gaps | Add explainable analysis services and deterministic scoring contracts. |
| 8–9 | Roadmaps and project recommendations | Add recommendation services with transparent inputs and citations. |
| 10–16 | Dashboard, auth, OCR, RAG, interviews, tracker, versions | Add authenticated resource ownership, background-ready boundaries, retrieval, simulations, and version history. |
| 17–19 | Audit, containers, deployment, documentation | Add test coverage gates, security review, Docker files, operational docs. |

## Decisions made now

The frontend is **Next.js with TypeScript and Tailwind CSS** as requested. The backend is **FastAPI with Pydantic and SQLAlchemy-ready modules**. PostgreSQL is deliberately deferred until Phase 2 to preserve the requested sequence. The project does not add Docker, OCR, embeddings, an LLM API client, or a database schema in this phase.
