from typing import Any, Callable, Dict, Tuple, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

class RetryCallState:
    attempt_number: int
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    outcome: Any | None

def retry(*, stop: Any, wait: Any, retry: Any, reraise: bool = ...) -> Callable[[F], F]: ...
def stop_after_attempt(attempt_number: int) -> Any: ...
def wait_random_exponential(*, max: int | float | None = ...) -> Any: ...
def wait_none() -> Any: ...
