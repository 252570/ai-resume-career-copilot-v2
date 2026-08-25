#!/usr/bin/env bash
set -u

cd "$(dirname "$0")/.."

pnpm install --frozen-lockfile > /tmp/copilot_pnpm_install.log 2>&1
install_status=$?

if [ "$install_status" -eq 0 ]; then
  (
    cd backend
    python3 -m pip install -r requirements.txt > /tmp/copilot_pip_install.log 2>&1
  )
fi
backend_install_status=$?

if [ "$install_status" -eq 0 ] && [ "$backend_install_status" -eq 0 ]; then
  (
    cd backend
    python3 -m pytest -q > /tmp/copilot_backend_tests.log 2>&1
  )
fi
backend_status=$?

if [ "$install_status" -eq 0 ]; then
  pnpm --filter career-copilot-frontend check > /tmp/copilot_frontend_check.log 2>&1
fi
check_status=$?

if [ "$install_status" -eq 0 ]; then
  pnpm build > /tmp/copilot_build.log 2>&1
fi
build_status=$?

printf 'install_status=%s backend_install_status=%s backend_status=%s frontend_check_status=%s build_status=%s\n' \
  "$install_status" "$backend_install_status" "$backend_status" "$check_status" "$build_status"

printf '\n--- backend tests ---\n'
tail -80 /tmp/copilot_backend_tests.log 2>/dev/null || true
printf '\n--- frontend check ---\n'
tail -80 /tmp/copilot_frontend_check.log 2>/dev/null || true
printf '\n--- production build ---\n'
tail -120 /tmp/copilot_build.log 2>/dev/null || true

if [ "$install_status" -ne 0 ] || [ "$backend_install_status" -ne 0 ] || [ "$backend_status" -ne 0 ] || [ "$check_status" -ne 0 ] || [ "$build_status" -ne 0 ]; then
  exit 1
fi
