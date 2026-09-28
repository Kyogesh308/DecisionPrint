class DecisionPrintError(Exception): pass
class LLMUnavailableError(DecisionPrintError): pass
class NotFoundError(DecisionPrintError): pass
class ScopeError(DecisionPrintError): pass
class MemoryUnavailableError(DecisionPrintError): pass
class ExtractionError(DecisionPrintError): pass
class ValidationFailedError(DecisionPrintError): pass
