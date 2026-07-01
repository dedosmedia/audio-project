"""Custom exception hierarchy for the intercom project.

Never let raw RuntimeError/ValueError leak out of audio or service code:
raise one of these instead so callers can distinguish failure domains.
"""


class IntercomError(Exception):
    """Base class for all intercom-specific errors."""


class ConfigError(IntercomError):
    """Raised when configuration is missing, malformed, or invalid."""


class PipelineError(IntercomError):
    """Raised when a GStreamer pipeline fails to build, start, or run."""


class ServiceError(IntercomError):
    """Raised when a Service fails to start, stop, or restart correctly."""
