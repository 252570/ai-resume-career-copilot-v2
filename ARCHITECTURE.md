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

| Module | Responsibility through Phase 3 | Future extension boundary |
| --- | --- | --- |
| `frontend/app` | Present the responsive product shell plus a central-configuration resume upload and parsed-evidence flow. | Dashboard, authenticated routes, job-analysis views, and tracking. |
| `backend/app/api/v1` | Expose health plus multipart resume upload and safe metadata retrieval routes. | Job, analysis, roadmap, recommendation, interview, and application routes. |
| `backend/app/schemas` | Define Pydantic contracts separately from persisted entities. | Resource contracts and explainability payloads. |
| `backend/app/core` | Centralize validated configuration and safe database configuration errors. | Logging, security settings, and provider configuration. |
| `backend/app/db` | Provide SQLAlchemy metadata, lazy engine construction, and request session lifecycle. | Transaction middleware and read/write splitting if later required. |
| `backend/app/models` | Define normalized PostgreSQL entities plus nullable parsed resume text and data fields. | User-isolated features and later analysis entities. |
| `backend/app/repositories` | Keep simple persistence lookup and resume staging operations outside API routes. | Feature-specific service orchestration. |
| `backend/app/services` | Validate supported files, generate safe storage keys, extract readable text, and parse deterministic signals. | OCR adapters and AI-assisted structured extraction. |
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
| 3 | Resume upload and deterministic parsing | **Complete:** validated PDF/DOCX/TXT upload, generated-name local storage, text extraction, basic signal parsing, focused migration, and retrieval contract. |
| 4 | Resume intelligence/extraction | Add richer normalized extraction, validation feedback, and user-confirmable structured resume records. |
| 5–7 | Job analysis, matching, ATS gaps | Add explainable analysis services and deterministic scoring contracts. |
| 8–9 | Roadmaps and project recommendations | Add recommendation services with transparent inputs and citations. |
| 10–16 | Dashboard, auth, OCR, RAG, interviews, tracker, versions | Add authenticated resource ownership, background-ready boundaries, retrieval, simulations, and version history. |
| 17–19 | Audit, containers, deployment, documentation | Add test coverage gates, security review, Docker files, operational docs. |

## Decisions made now

The frontend is **Next.js with TypeScript and Tailwind CSS** as requested. The backend is **FastAPI with Pydantic, SQLAlchemy, Alembic, and a PostgreSQL connection boundary**. Database credentials are runtime-only through `DATABASE_URL`. Phase 3 stores original uploads outside PostgreSQL with generated keys and stores only metadata, extracted text, and deterministic parsed values in the resume record. The project deliberately does not add matching execution, embeddings, OCR, an LLM API client, authentication, or Docker in this phase.
