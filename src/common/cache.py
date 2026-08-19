"""A deliberately small in-process cache.

Not thread safe, not distributed, and not intended to become either.
Anything that needs more than this should talk to Redis directly.
"""

import time
from typing import Any, Callable

_store: dict[str, tuple[float, Any]] = {}
_DEFAULT_TTL_S = 300


def cache_put(key: str, value: Any, ttl_s: int = _DEFAULT_TTL_S) -> None:
    _store[key] = (time.monotonic() + ttl_s, value)


def cache_get(key: str) -> Any | None:
    entry = _store.get(key)
    if entry is None:
        return None
    expires_at, value = entry
    if expires_at < time.monotonic():
        del _store[key]
        return None
    return value


def cache_drop(prefix: str) -> int:
    """Remove every entry whose key starts with prefix. Returns the count."""
    doomed = [k for k in _store if k.startswith(prefix)]
    for key in doomed:
        del _store[key]
    return len(doomed)


def get_or_fetch(key: str, fetcher: Callable[[], Any]) -> Any:
    """Return the cached value for key, or call fetcher and cache the result."""
    cached = cache_get(key)
    if cached is not None:
        return cached
    ...
