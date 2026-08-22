"""Application-specific exceptions that avoid exposing sensitive connection details."""


class DatabaseConfigurationError(RuntimeError):
    """Raised when database operations are attempted without valid PostgreSQL configuration."""


class ResumeUploadError(ValueError):
    """Safe, user-facing validation failure for an uploaded resume."""

    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
