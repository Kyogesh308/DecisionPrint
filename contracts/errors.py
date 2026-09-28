class DecisionPrintError(Exception):
    """Base error for DecisionPrint."""


class ScopeError(DecisionPrintError):
    """User role lacks access to the requested resource."""


class NotFoundError(DecisionPrintError):
    """Requested resource not found."""


class MemoryUnavailableError(DecisionPrintError):
    """Hindsight memory backend is unreachable."""


class LLMUnavailableError(DecisionPrintError):
    """LLM provider is unavailable."""


class ExtractionError(DecisionPrintError):
    """Decision or outcome extraction failed."""


class ValidationFailedError(DecisionPrintError):
    """Generated data failed validation."""
