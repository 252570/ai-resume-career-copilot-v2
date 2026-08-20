# Phase 2 Database Foundation

The database layer uses **PostgreSQL**, **SQLAlchemy 2.x**, **Alembic**, and **Pydantic**. SQLAlchemy models in `backend/app/models/` define persistence; Pydantic schemas in `backend/app/schemas/` define external validation and serialization. This separation prevents API contracts from being coupled to database implementation details.

## Relationship map

```text
User 1 ── * Resume 1 ── * ResumeSkill * ── 1 Skill
User 0..1 ── * Job    1 ── * JobSkill    * ── 1 Skill
Resume 1 ── * MatchResult * ── 1 Job
```

| Concern | Phase 2 decision |
| --- | --- |
| Identity | UUID primary keys are generated in the application layer. |
| Ownership | `User → Resume` deletes orphaned resume metadata; `Job.user_id` becomes `NULL` if an owner is deleted. |
| Resume files | Only immutable metadata and a future storage key are persisted; document bytes are deliberately excluded. |
| Skills | Canonical skill names are unique and indexable, enabling future normalized extraction and matching. |
| Join tables | `ResumeSkill` and `JobSkill` use composite primary keys to prevent duplicate associations. |
| Match results | A unique resume/job/analysis-version key prevents accidental duplicate analysis records, but no matching logic is implemented yet. |
| Database URL | Database credentials come from `DATABASE_URL` at runtime only. |

## Migration workflow

```bash
cd backend
python3 -m alembic revision --autogenerate -m "describe change"
python3 -m alembic upgrade head
python3 -m alembic downgrade -1
```

Review generated migration files before applying them to a non-local PostgreSQL database. Database model changes must be accompanied by a migration and model tests.
