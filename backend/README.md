# Backend

The API is a standalone FastAPI service. Phase 1 intentionally exposes only a typed, versioned health endpoint; PostgreSQL, SQLAlchemy models, routes for user content, and AI providers are deferred.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
python3 -m pytest
```

Visit `http://localhost:8000/docs` to inspect the OpenAPI contract and `http://localhost:8000/api/v1/health` to verify service health.

The runtime expects an optional local `.env` file for non-secret configuration. Phase 1 defaults are safe for local verification: `APP_NAME=AI Resume & Career Copilot API`, `APP_ENV=development`, and `API_V1_PREFIX=/api/v1`. Future credentials and database connection strings will remain environment-only and will be documented when the relevant phase begins.
