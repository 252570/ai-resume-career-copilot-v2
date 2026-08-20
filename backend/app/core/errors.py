"""Application-specific exceptions that avoid exposing sensitive connection details."""


class DatabaseConfigurationError(RuntimeError):
    """Raised when database operations are attempted without valid PostgreSQL configuration."""
