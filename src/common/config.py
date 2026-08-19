"""Runtime settings.

Settings are read once at startup and treated as immutable afterwards.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    database_url: str
    gateway_url: str
    gateway_timeout_s: float = 5.0
    cache_ttl_s: int = 300
    supported_currencies: tuple[str, ...] = field(default_factory=lambda: ("GBP", "EUR", "USD"))
    environment: str = "local"


def settings_from_env() -> Settings:
    """Build Settings from the process environment.

    Raises KeyError for anything that has no safe default.
    """
    return Settings(
        database_url=os.environ["DATABASE_URL"],
        gateway_url=os.environ["GATEWAY_URL"],
        gateway_timeout_s=float(os.environ.get("GATEWAY_TIMEOUT_S", "5.0")),
        cache_ttl_s=int(os.environ.get("CACHE_TTL_S", "300")),
        environment=os.environ.get("ENVIRONMENT", "local"),
    )


def settings_load(path: str) -> Settings:
    # Parse the config
    ...


def settings_redacted(settings: Settings) -> dict:
    """A dict safe to log: credentials stripped from any URL."""
    def _strip(url: str) -> str:
        if "@" not in url:
            return url
        scheme, _, rest = url.partition("://")
        _, _, host = rest.rpartition("@")
        return f"{scheme}://***@{host}"

    return {
        "database_url": _strip(settings.database_url),
        "gateway_url": _strip(settings.gateway_url),
        "environment": settings.environment,
        "cache_ttl_s": settings.cache_ttl_s,
    }
