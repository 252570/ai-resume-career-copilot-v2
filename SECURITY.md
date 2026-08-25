# Security Policy

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Report privately through GitHub's [Report a vulnerability](https://github.com/252570/ai-resume-career-copilot-v2/security/advisories/new) form, which opens a draft advisory visible only to the maintainer.

Include what you need to make the issue reproducible: affected endpoint or file, the steps involved, and what an attacker gains. This is a student project maintained by one person, so expect an initial reply within about a week rather than same-day. If a fix is warranted, the advisory is published alongside it with credit unless you prefer otherwise.

## Supported versions

Only the `main` branch receives fixes. There are no published release artifacts or backported patches.

## What is in scope

The application code in this repository: the FastAPI backend, the Next.js frontend, the deterministic parsing and matching services, and the Alembic migrations. Authentication and owner-scoping bugs are the highest-value reports — anything that lets one account read or modify another account's resumes, jobs, analyses, practice sessions, or applications.

## What is out of scope

- Findings that require a secret the project never commits (see below). A report premised on knowing `DATABASE_URL` or `JWT_SECRET` is not a vulnerability in this codebase.
- The absence of deliberately deferred features. OCR, LLM providers, RAG, semantic embeddings, and deployment packaging are documented as not implemented in [README.md](README.md); missing hardening for code that does not exist is not a finding.
- Free-tier hosting behavior, such as the backend cold-starting after inactivity.
- Automated scanner output with no demonstrated impact on this application.

## Secrets and configuration

No credentials, API keys, password hashes, or signing secrets are committed. Configuration is environment-only:

- `backend/env.example` and `frontend/env.example` document the contract with placeholders.
- Real values live in `backend/.env` and `frontend/.env.local`, both gitignored.
- `DATABASE_URL` and `JWT_SECRET` have no defaults. The API fails closed with a controlled error rather than falling back to an insecure value, and `JWT_SECRET` is rejected below 32 characters.

Generate a signing secret per environment and never reuse one across environments:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

If you believe a secret was committed at any point, report it privately using the process above rather than opening an issue.

## Handling of user data

Resume files are user-supplied documents and are treated as untrusted input: uploads are restricted by extension, verified against a file signature, and capped at 5 MB. Parsing is deterministic regex and section-boundary extraction — no document content is sent to a third-party service. The API never returns password hashes, upload storage paths, or raw source bytes, and the browser holds only the bearer token for the active session.

Because this is a student project rather than an operated service, **do not upload a real resume or reuse a real password** on any deployment of it.
