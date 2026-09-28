from typing import Protocol, Optional
from .models import Scope, ReflectResult

class ReflectFn(Protocol):
    def __call__(self, question: str, scope: Scope, *, context: Optional[str] = None) -> ReflectResult:
        ...
