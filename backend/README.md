# Backend

The API is a standalone FastAPI service. Phase 2 introduces a PostgreSQL-ready persistence layer with SQLAlchemy ORM models, Alembic migrations, Pydantic data contracts, and a narrow repository boundary. The public API intentionally remains limited to the health route: file upload, parsing, matching, AI features, and user-authenticated data routes are deferred.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy the non-secret template and update DATABASE_URL locally.
cp env.example .env
python3 -m alembic upgrade head

uvicorn app.main:app --reload --port 8000
python3 -m pytest
```

Visit `http://localhost:8000/docs` to inspect the OpenAPI contract and `http://localhost:8000/api/v1/health` to verify service health.

The runtime requires `DATABASE_URL` before a database-backed operation can begin. It accepts only `postgresql://` or `postgresql+psycopg://` URLs and emits a safe configuration error if unset or invalid. Keep the real value in a private environment file locally or deployment secret store in production.

The first migration is revision `20260820_0001`. Verify its generated PostgreSQL DDL without connecting to a server as follows:

```bash
DATABASE_URL='postgresql+psycopg://career_copilot:placeholder@localhost:5432/career_copilot' \
  python3 -m alembic upgrade head --sql
```
