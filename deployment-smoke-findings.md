# Deployment smoke findings

## Local development boundary

The local Next.js development page at `http://127.0.0.1:3000` rendered successfully. When no `NEXT_PUBLIC_API_BASE_URL` is present, it intentionally shows the service-boundary state that asks the operator to configure the FastAPI `/api/v1` address.

## Production static export

A production build with `NEXT_PUBLIC_API_BASE_URL=https://career-copilot-api-1t3l.onrender.com/api/v1` rendered successfully when served from the generated `frontend/out` directory. The browser showed the private workspace signup form with display name, email, password, create-workspace, and existing-account controls. The configured API origin was confirmed in the generated JavaScript bundle.

## Public endpoint observation

The reachable API host `https://career-copilot-api-1t3l.onrender.com/api/v1/health` returned HTTP 200 and reported `database: connected` on 2026-08-25. The Render hostname declared in the current Blueprint (`career-copilot-api.onrender.com`) returned a platform 404 during the same probe, and `https://career-copilot.onrender.com` also returned 404. The existing public API rejected a CORS preflight from `https://career-copilot.onrender.com`, so the Blueprint’s exact frontend origin must be deployed and configured together before browser uploads can work.
