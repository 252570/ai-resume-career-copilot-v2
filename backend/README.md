# Backend

The API is a standalone FastAPI service. Phase 3 adds PDF, DOCX, and TXT resume upload, secure generated-name local storage, deterministic text extraction, conservative basic signal parsing, and metadata retrieval. Matching, AI features, user authentication, OCR, and original-file download routes remain deferred.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Copy the non-secret template and update DATABASE_URL locally.
cp env.example .env
python3 -m alembic upgrade head

python -m uvicorn app.main:app --reload --port 8001
python -m pytest
```

Visit `http://127.0.0.1:8001/docs` to inspect the OpenAPI contract and `http://127.0.0.1:8001/api/v1/health` to verify service health.

The runtime requires `DATABASE_URL` before a database-backed operation can begin. It accepts only `postgresql://` or `postgresql+psycopg://` URLs and emits a safe configuration error if unset or invalid. Keep the real value in a private environment file locally or deployment secret store in production.

Run `python -m alembic upgrade head` before uploading. Migration `20260822_0002` adds only nullable `extracted_text` and `parsed_data` fields to the established `resumes` table and makes `user_id` optional until authentication is introduced. Verify its generated PostgreSQL DDL without connecting to a server as follows:

```bash
DATABASE_URL='postgresql+psycopg://career_copilot:placeholder@localhost:5432/career_copilot' \
  python3 -m alembic upgrade head --sql
```

### Upload contract

`POST /api/v1/resumes/upload` accepts multipart field `file` and returns `201 Created` after validation, generated-name storage, extraction, deterministic parsing, and metadata persistence. Supported types are PDF, DOCX, and UTF-8/UTF-16 TXT. The hard limit is 5 MB. Unsupported or unreadable input returns an actionable `400` response; oversized files return `413`; persistence errors return a generic `500` response without stack traces or credentials.

`GET /api/v1/resumes/{resume_id}` returns parsed metadata but never returns the original binary upload or its storage path.

Local uploads reside in `backend/storage/resumes/`. Each filename is a generated UUID plus a validated extension, and the directory contents are ignored by Git.
