# Deployment smoke findings

## Local development boundary

The local Next.js development page at `http://127.0.0.1:3000` rendered successfully. When no `NEXT_PUBLIC_API_BASE_URL` is present, it intentionally shows the service-boundary state that asks the operator to configure the FastAPI `/api/v1` address.

## Production static export

A production build with `NEXT_PUBLIC_API_BASE_URL=https://career-copilot-api-1t3l.onrender.com/api/v1` rendered successfully when served from the generated `frontend/out` directory. The browser showed the private workspace signup form with display name, email, password, create-workspace, and existing-account controls. The configured API origin was confirmed in the generated JavaScript bundle.

## Public endpoint observation

The reachable API host `https://career-copilot-api-1t3l.onrender.com/api/v1/health` returned HTTP 200 and reported `database: connected` on 2026-08-25. The Render hostname declared in the current Blueprint (`career-copilot-api.onrender.com`) returned a platform 404 during the same probe, and `https://career-copilot.onrender.com` also returned 404. The existing public API rejected a CORS preflight from `https://career-copilot.onrender.com`, so the Blueprint’s exact frontend origin must be deployed and configured together before browser uploads can work.

## Permanent hosting access

The Render dashboard redirected to `https://dashboard.render.com/login` and presented GitHub, GitLab, Bitbucket, Google, and email sign-in options. No authenticated Render workspace was available in the current browser session, so permanent deployment cannot be completed until the user signs in or provides a connected deployment path.

## Authenticated Render workspace

The connected My Browser session is authenticated to Render and shows `My Workspace`, with one existing active service named `career-copilot-api` in Ohio. The Blueprints area had no existing Blueprint instances. A new Blueprint was started from the GitHub repository on the `main` branch with name `career-copilot-production`. Render detected `render.yaml` but displayed an issue warning: preview environments are unavailable for Hobby workspaces, and the page currently shows a `Retry` control while loading/reviewing the Blueprint.

## Blueprint deployment

The authenticated Render workspace accepted the repository Blueprint after the unsupported Hobby preview setting was removed. Blueprint `career-copilot-production` was created with ID `exs-da6ocbv10e5c73cbk4bg`; the sync for commit `accc464` created services named `career-copilot-api-la6y` and `career-copilot-la6y`. Render currently reports the sync as `Running`, so the live URLs must be checked after service provisioning finishes.

## Render redeploy failure

The new API service URL is `https://career-copilot-api-la6y.onrender.com`. The first deployment failed because Alembic could not parse the supplied `DATABASE_URL`. After the URL trimming fix was pushed, a manual redeploy for commit `9c39038` also failed with status 1 during the build. Render’s application-log view is unavailable for failed deploys; the deployment detail page must be used for the build log. The service remains unavailable until the database secret is corrected or re-entered.

## Diagnosis of Render migration failure

The sanitized equivalent of the supplied Neon-style URL parses correctly with SQLAlchemy, including `sslmode=require` and `channel_binding=require`. Render’s build still fails before normalization at `make_url(DATABASE_URL)`, which indicates the value currently stored in Render is not the expected complete PostgreSQL URL or contains malformed copied content. The repository now trims surrounding whitespace and adds a regression test, but the Render environment value should be re-entered from Neon’s Connect dialog as a complete URI.

## Render environment correction

The authenticated Render API service environment editor was opened and the `DATABASE_URL` field was replaced directly in the browser with the user-provided Neon connection string. The secret was not written to the repository or notes. Render’s editor now shows the value as a masked secret and offers `Save, rebuild, and deploy`.

## Render URL simplification

The Render API environment editor was reopened and the `DATABASE_URL` value was simplified to the same Neon endpoint with `sslmode=require` only, removing the optional `channel_binding` query parameter. The value remains stored only as a masked Render secret.

## Final parser diagnosis

Render’s latest deployment still reaches `backend/alembic/env.py:33`, where `make_url(database_url)` is called before `normalize_database_url(database_url)`. The sanitizer therefore never runs for malformed copied values. The next patch will normalize first and then validate the normalized scheme, allowing quoted or escaped-newline provider URLs to be accepted before SQLAlchemy parses them.

## Explicit driver correction

The Render API environment editor now contains the Neon connection string with the explicit `postgresql+psycopg://` scheme and `sslmode=require`. This avoids ambiguity in both SQLAlchemy and Alembic while keeping the credential masked in Render.

## Provisioned Render services

The Blueprint resources page shows both services provisioned: API `career-copilot-api-la6y` in Oregon and static frontend `career-copilot-la6y` globally. Render lists the frontend URL as `https://career-copilot-la6y.onrender.com` and the API URL as `https://career-copilot-api-la6y.onrender.com`. The connected browser could not open the frontend URL due a browser connection error, so shell-level HTTP verification is required. Render’s event list currently reports the static deployment as failed for the old `dd8bdc4` commit because the API migration deployment failed; the frontend URL still needs independent HTTP verification.

## Live deployment comparison

The existing API service `https://career-copilot-api-1t3l.onrender.com` responds with HTTP 200 for both liveness and readiness, reporting a connected database. The new Blueprint API remains unavailable because its latest deployment failed. The new static site `https://career-copilot-la6y.onrender.com` responds with HTTP 404 and `x-render-routing: static-no-asset`, indicating that its publish directory contains no deployed asset. The static service settings confirm the repository and `main` branch, but the build and publish values require further inspection or correction.

## Frontend is live

Render successfully published the permanent static site at `https://career-copilot-la6y.onrender.com` from commit `fe84ffb`. The build completed with Next.js static export and Render reported `Your site is live`. The frontend’s configured API origin still needs verification and correction: the Blueprint currently references the unsuffixed host `career-copilot-api.onrender.com`, while the provisioned API service is `career-copilot-api-la6y.onrender.com` and the known healthy legacy API is `career-copilot-api-1t3l.onrender.com`.

## Frontend API origin correction

The permanent frontend’s Render environment variable `NEXT_PUBLIC_API_BASE_URL` was corrected to the known healthy API origin `https://career-copilot-api-1t3l.onrender.com/api/v1`. The previous build had embedded the invalid unsuffixed `career-copilot-api.onrender.com` hostname in the Content Security Policy and API client configuration.

## Existing API CORS update

The healthy existing API at `https://career-copilot-api-1t3l.onrender.com` responds with HTTP 200 and a connected database, but its response to the permanent frontend origin lacks `access-control-allow-origin`. The existing API service’s `CORS_ORIGINS` is being updated to `https://career-copilot-la6y.onrender.com`; its existing database and JWT secrets remain unchanged.

## 2026-08-25 production follow-up

- The permanent static frontend initially rendered blank because the deployed CSP blocked Next.js inline hydration bootstrap scripts. Commit `edc6189` changed only `script-src` to allow `'unsafe-inline'`; the live frontend now renders the signup page and authenticated dashboard.
- The healthy legacy API is the current production backend fallback at `career-copilot-api-1t3l.onrender.com`. Its CORS allowlist now preserves the prior Manus origin and includes the permanent Render frontend origin. GET and OPTIONS probes return the expected `Access-Control-Allow-Origin`, methods, and headers.
- The legacy API had no database tables because its Render Build Command omitted migrations. Render was updated to run `python -m alembic upgrade head` after dependency installation; the production database is now schema-initialized.
- The legacy API also lacked `JWT_SECRET`; a fresh secret was generated and saved only in Render’s environment. It was not written to the repository or this log.
- A synthetic browser signup completed successfully and opened the owner-scoped dashboard.
- The authenticated Jobs workflow successfully parsed and saved a synthetic Backend Engineer role, then navigated to Match with the saved role available in the selector.
- After sign-out, the same synthetic account logged back in successfully through the public frontend and the saved role remained available, confirming persistence and token-based access.
- No passwords, database URLs, JWT values, or user credentials are recorded in this file.
