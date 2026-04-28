"""Layer 3 — retry with exponential backoff.

Wrap any function that calls an external service (Bedrock, S3, Stripe, …)
and it gets retry behavior for free. Transient errors → wait + retry.
Permanent errors → fail fast (no point retrying a wrong input).
"""
import time
import functools
from typing import Iterable


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    retryable_errors: Iterable[str] = (),
):
    """Decorator: retry on transient errors only. Fail fast on everything else.

    Args:
        max_retries: how many times to retry before giving up (3 is fine for most APIs).
        base_delay: seconds to wait before the first retry. Doubles each attempt.
        retryable_errors: error class names worth retrying. Anything else
            propagates immediately so the caller sees the real error.

    Example:
        >>> @retry_with_backoff(
        ...     max_retries=3,
        ...     base_delay=1.0,
        ...     retryable_errors=["ThrottlingException"],
        ... )
        ... def my_api_call(...): ...
    """
    retryable = set(retryable_errors)

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    err_name = e.__class__.__name__
                    # Permanent error? Don't retry — fail fast.
                    if err_name not in retryable:
                        raise
                    # Out of retries? Give up.
                    if attempt >= max_retries:
                        raise
                    # Transient → wait + retry, with exponential backoff.
                    delay = base_delay * (2 ** attempt)
                    print(f"[retry] {err_name} on attempt {attempt + 1}, "
                          f"waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator
