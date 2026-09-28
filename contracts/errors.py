class DecisionPrintError(Exception):
    """Base error for DecisionPrint."""


class ScopeError(DecisionPrintError):
    """User role lacks access to the requested resource."""


class NotFoundError(DecisionPrintError):
    """Requested resource not found."""


class MemoryUnavailableError(DecisionPrintError):
    """Hindsight memory backend is unreachable."""
