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

## Deferred Phase 2 — PostgreSQL Database Foundation

- [ ] Inspect the Phase 1 backend, dependency state, and PostgreSQL availability.
- [ ] Finalize the user-profile and resume-storage metadata model.
- [ ] Add SQLAlchemy models, database session management, repositories, and Alembic migration support.
- [ ] Configure and apply the PostgreSQL schema without introducing document upload or parsing.
- [ ] Add database-focused tests and verify the migration, API health, and test suite.
- [ ] Document the completed Phase 2 foundation and stop for Phase 3 approval.
