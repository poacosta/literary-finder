"""Retry mechanism with exponential backoff for failed operations."""

import time
import random
import logging
from typing import Callable, TypeVar, Optional, Any, List, Type, Union
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str, last_exception: Exception, attempts: int):
        super().__init__(message)
        self.last_exception = last_exception
        self.attempts = attempts


def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_factor: float = 2.0,
    jitter: bool = True,
    retry_on_exceptions: Optional[Union[Type[Exception], List[Type[Exception]]]] = None,
    backoff_on_exceptions: Optional[Union[Type[Exception], List[Type[Exception]]]] = None
):
    """
    Decorator that implements exponential backoff retry mechanism.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_factor: Multiplier for each retry delay
        jitter: Add random jitter to prevent thundering herd
        retry_on_exceptions: Specific exceptions to retry on (default: all)
        backoff_on_exceptions: Exceptions that should trigger backoff (default: all)
    """
    if retry_on_exceptions and not isinstance(retry_on_exceptions, list):
        retry_on_exceptions = [retry_on_exceptions]
    
    if backoff_on_exceptions and not isinstance(backoff_on_exceptions, list):
        backoff_on_exceptions = [backoff_on_exceptions]
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry on this exception
                    if retry_on_exceptions and not any(isinstance(e, exc_type) for exc_type in retry_on_exceptions):
                        logger.warning(f"Not retrying {func.__name__} due to non-retryable exception: {e}")
                        raise e
                    
                    # If this is the last attempt, raise the exception
                    if attempt == max_retries:
                        logger.error(f"All retry attempts exhausted for {func.__name__}. Last error: {e}")
                        raise RetryError(
                            f"Failed after {max_retries + 1} attempts", 
                            e, 
                            attempt + 1
                        )
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_factor ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    # Check if we should apply backoff for this exception
                    should_backoff = True
                    if backoff_on_exceptions and not any(isinstance(e, exc_type) for exc_type in backoff_on_exceptions):
                        should_backoff = False
                        delay = 0.1  # Minimal delay for non-backoff exceptions
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise RetryError(f"Unexpected error in retry logic", last_exception, max_retries + 1)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry on this exception
                    if retry_on_exceptions and not any(isinstance(e, exc_type) for exc_type in retry_on_exceptions):
                        logger.warning(f"Not retrying {func.__name__} due to non-retryable exception: {e}")
                        raise e
                    
                    # If this is the last attempt, raise the exception
                    if attempt == max_retries:
                        logger.error(f"All retry attempts exhausted for {func.__name__}. Last error: {e}")
                        raise RetryError(
                            f"Failed after {max_retries + 1} attempts", 
                            e, 
                            attempt + 1
                        )
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_factor ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    # Check if we should apply backoff for this exception
                    should_backoff = True
                    if backoff_on_exceptions and not any(isinstance(e, exc_type) for exc_type in backoff_on_exceptions):
                        should_backoff = False
                        delay = 0.1  # Minimal delay for non-backoff exceptions
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            raise RetryError(f"Unexpected error in retry logic", last_exception, max_retries + 1)
        
        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_api_call(
    func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    *args,
    **kwargs
) -> T:
    """
    Utility function to retry API calls without using decorator syntax.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        Result of the successful function call
        
    Raises:
        RetryError: If all retry attempts are exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(f"All retry attempts exhausted for {func.__name__}. Last error: {e}")
                raise RetryError(
                    f"Failed after {max_retries + 1} attempts", 
                    e, 
                    attempt + 1
                )
            
            delay = base_delay * (2 ** attempt)
            delay *= (0.5 + random.random() * 0.5)  # Add jitter
            
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            
            time.sleep(delay)
    
    # This should never be reached
    raise RetryError(f"Unexpected error in retry logic", last_exception, max_retries + 1)