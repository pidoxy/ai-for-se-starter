"""Application error hierarchy.

Every failure that crosses a module boundary is raised as one of these.
See docs/adr/0003-typed-exceptions.md for the reasoning.
"""


class AppError(Exception):
    """Base for all application errors. Never raise this directly."""

    def __init__(self, message: str, *, context: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:  # pragma: no cover - trivial
        if not self.context:
            return self.message
        detail = ", ".join(f"{k}={v!r}" for k, v in sorted(self.context.items()))
        return f"{self.message} ({detail})"


class NotFoundError(AppError):
    """A requested entity does not exist."""


class ValidationError(AppError):
    """Input failed a business rule or a shape check."""


class UpstreamError(AppError):
    """A dependency we do not own failed or answered unusably."""


class ConflictError(AppError):
    """The request is well formed but conflicts with current state."""
