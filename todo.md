# Current Work — Deployment Recovery

- [x] Inspect root and frontend package manifests, lockfiles, and workspace configuration.
- [x] Make root installation include the nested Next.js application dependencies.
- [x] Reproduce the cloud deployment build from the frozen root workspace dependency graph.
- [x] Confirm the corrected production build succeeds and document the recovery.

## Current Work — Deployment Artifact Recovery

- [x] Inspect the current Next.js output and root deployment artifact expectation.
- [x] Configure the frontend to emit a deployable standalone artifact into root `dist/`.
- [x] Verify the root build creates `dist/` and that the standalone server starts successfully.

## Current Work — Header Brand Mark

- [x] Inspect the top-left brand mark and its unavailable managed image route.
- [x] Replace the fragile image dependency with a durable visual mark.
- [x] Verify the header mark is visible in the frontend preview and production build.

## Current Work — Managed Deployment Configuration

- [x] Inspect the managed runtime configuration and determine why it is absent from the root artifact.
- [x] Include the required configuration in the root `dist/` package without exposing secrets.
- [x] Verify the artifact includes the managed deployment configuration alongside `dist/server.js`.

## Current Work — Phase 2 PostgreSQL Database Foundation

- [x] Inspect the backend architecture, current frontend boundary, and local PostgreSQL prerequisites.
- [x] Define normalized models, foreign keys, uniqueness constraints, and indexes for User, Resume, Job, Skill, ResumeSkill, JobSkill, and MatchResult.
- [x] Add SQLAlchemy database configuration, engine/session lifecycle, models, Pydantic schemas, repositories, and error handling.
- [x] Configure Alembic and create an initial PostgreSQL migration.
- [x] Verify PostgreSQL migration SQL generation, database configuration, model behavior, backend tests, and the untouched frontend build.
- [x] Update database setup documentation and stop for Phase 3 approval.

## Current Work — Phase 2 PostgreSQL Runtime Verification

- [x] Inspect current migration configuration and local PostgreSQL client/server availability.
- [ ] Configure a local development PostgreSQL connection exclusively through environment variables when supported. *(Blocked: no local PostgreSQL client/server is installed, and the injected DATABASE_URL is not PostgreSQL.)*
- [ ] Apply migration `20260820_0001` and verify all seven Phase 2 tables. *(Blocked pending a reachable PostgreSQL DATABASE_URL.)*
- [x] Rerun database tests and report the concrete connection, migration, table, and test status.

## Current Work — Windows 11 PostgreSQL Guide

- [x] Review the existing database documentation and configuration conventions.
- [x] Add a Windows 11 PostgreSQL installation, database/user creation, `.env`, migration, verification, and troubleshooting guide.
- [x] Confirm that the guide contains no real credentials and does not alter Phase 2 code or start Phase 3.

## Current Work — Phase 3 Resume Upload and Parsing

- [x] Inspect the existing backend, Resume schema/migration, frontend structure, and current dependencies.
- [x] Define secure PDF/DOCX/TXT upload validation, local storage, deterministic parsing, and persistence boundaries.
- [x] Implement upload and retrieval APIs with focused schema changes, error handling, storage safety, and tests.
- [x] Implement the existing-design-compatible frontend upload and parsed-result experience through a centralized API configuration.
- [x] Verify migration DDL, backend tests, frontend build, preserved UI, and Phase 3 documentation.
