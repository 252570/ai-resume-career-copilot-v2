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
│ users · resumes · jobs · skills · match_results           │
└─────────────────────────────────────────────────────────┘
```

## Current modules

| Module | Responsibility through Phase 2 | Future extension boundary |
| --- | --- | --- |
| `frontend/app` | Present the responsive product shell and Phase 1 state. | Dashboard, upload flows, result visualizations, authenticated routes. |
| `backend/app/api/v1` | Expose versioned HTTP routing and service health. | Resume, jobs, analyses, roadmaps, recommendations, interviews, applications. |
| `backend/app/schemas` | Define Pydantic contracts separately from persisted entities. | Resource contracts and explainability payloads. |
| `backend/app/core` | Centralize validated configuration and safe database configuration errors. | Logging, security settings, and provider configuration. |
| `backend/app/db` | Provide SQLAlchemy metadata, lazy engine construction, and request session lifecycle. | Transaction middleware and read/write splitting if later required. |
| `backend/app/models` | Define normalized PostgreSQL entities, constraints, indexes, and relationships. | Parsed resume fields and user-isolated features. |
| `backend/app/repositories` | Keep simple persistence lookup operations outside API routes. | Feature-specific service orchestration. |
| `backend/alembic` | Version PostgreSQL schema changes. | Future schema migrations for each planned phase. |
| `backend/tests` | Verify public health, database configuration, and important persistence relationships. | Integration, authorization, and security tests. |

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
| 2 | PostgreSQL and Alembic migrations | **Complete:** database session factory, SQLAlchemy models, Pydantic contracts, initial migration, repository boundary, and tests. |
| 3–4 | Resume upload, parsing, intelligence | Add private file storage abstraction, parser adapters, normalized resume schemas. |
| 5–7 | Job analysis, matching, ATS gaps | Add explainable analysis services and deterministic scoring contracts. |
| 8–9 | Roadmaps and project recommendations | Add recommendation services with transparent inputs and citations. |
| 10–16 | Dashboard, auth, OCR, RAG, interviews, tracker, versions | Add authenticated resource ownership, background-ready boundaries, retrieval, simulations, and version history. |
| 17–19 | Audit, containers, deployment, documentation | Add test coverage gates, security review, Docker files, operational docs. |

## Decisions made now

The frontend is **Next.js with TypeScript and Tailwind CSS** as requested. The backend is **FastAPI with Pydantic, SQLAlchemy, Alembic, and a PostgreSQL connection boundary**. Database credentials are runtime-only through `DATABASE_URL`. The project deliberately does not add document upload/parsing, matching execution, embeddings, OCR, an LLM API client, authentication, or Docker in Phase 2.
