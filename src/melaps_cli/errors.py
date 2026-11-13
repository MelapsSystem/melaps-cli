"""Typed errors for the Melaps CLI."""


class MelapsError(Exception):
    """Base error for all CLI failures."""


class AuthError(MelapsError):
    """The API key is missing, invalid, or expired."""


class NotFoundError(MelapsError):
    """The requested job, cluster, or reservation does not exist."""


class RateLimitError(MelapsError):
    """The API rate limit was hit. Retry after ``retry_after`` seconds."""

    def __init__(self, retry_after=60):
        super().__init__(f"rate limit exceeded, retry after {retry_after}s")
        self.retry_after = retry_after


class PreemptedError(MelapsError):
    """A batch job was preempted by a reserved workload."""
