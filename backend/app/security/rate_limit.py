from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status

_WINDOW_SECONDS = 15 * 60
_MAX_ATTEMPTS_PER_WINDOW = 10
_attempts: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_lock = Lock()


def _client_identifier(request: Request) -> str:
    # Do not trust arbitrary forwarded headers here. Render terminates TLS and
    # supplies the direct client connection to the application process.
    return request.client.host if request.client else "unknown-client"


def _check(key: tuple[str, str], now: float) -> None:
    window = _attempts[key]
    cutoff = now - _WINDOW_SECONDS
    while window and window[0] <= cutoff:
        window.popleft()
    if len(window) >= _MAX_ATTEMPTS_PER_WINDOW:
        retry_after = max(1, int(_WINDOW_SECONDS - (now - window[0])))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please wait and try again.",
            headers={"Retry-After": str(retry_after)},
        )
    window.append(now)


def reset_rate_limit_state() -> None:
    """Clear in-memory counters for deterministic tests and local development."""
    with _lock:
        _attempts.clear()


def enforce_auth_rate_limit(request: Request, email: str) -> None:
    """Limit authentication attempts by client and normalized email address.

    State is intentionally process-local and conservative. For a multi-instance
    deployment, move these counters to a shared store such as Redis before
    scaling horizontally.
    """
    now = monotonic()
    normalized_email = email.strip().lower()
    with _lock:
        _check(("ip", _client_identifier(request)), now)
        _check(("email", normalized_email), now)
