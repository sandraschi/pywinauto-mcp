"""
Common utilities and error handling for PyWinAuto MCP tools.
"""
import functools
import logging
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize logger
logger = logging.getLogger(__name__)

# Type variable for generic function typing
F = TypeVar('F', bound=Callable[..., Any])

class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = Field(False, description="Indicates if the operation was successful")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error that occurred")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = Field(True, description="Indicates if the operation was successful")
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

def handle_errors(func: F) -> Callable[..., Dict[str, Any]]:
    """
    Decorator to handle errors and standardize responses.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            
            # If the function already returned a response, return it as-is
            if isinstance(result, dict) and 'success' in result:
                return result
                
            # Otherwise, wrap the result in a success response
            return SuccessResponse(
                data={"result": result}
            ).dict()
            
        except Exception as e:
            error_type = e.__class__.__name__
            error_msg = str(e) or "An unknown error occurred"
            
            # Log the error with full traceback
            logger.error(
                f"Error in {func.__name__}: {error_msg}",
                exc_info=True,
                extra={
                    "error_type": error_type,
                    "function": func.__name__,
                    "args": args,
                    "kwargs": {k: v for k, v in kwargs.items() if k not in ['password', 'api_key']}
                }
            )
            
            # Return a standardized error response
            return ErrorResponse(
                error=error_msg,
                error_type=error_type
            ).dict()
    
    return wrapper

def log_execution(func: F) -> Callable[..., Any]:
    """
    Decorator to log function execution details.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with execution logging
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        logger.info(
            f"Starting execution of {func.__name__}",
            extra={
                "function": func.__name__,
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k not in ['password', 'api_key']}
            }
        )
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                f"Completed {func.__name__} in {duration:.2f} seconds",
                extra={
                    "function": func.__name__,
                    "duration_seconds": duration,
                    "success": True
                }
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error in {func.__name__} after {duration:.2f} seconds: {str(e)}",
                exc_info=True,
                extra={
                    "function": func.__name__,
                    "duration_seconds": duration,
                    "success": False,
                    "error": str(e),
                    "error_type": e.__class__.__name__
                }
            )
            raise
    
    return wrapper

def register_tool(
    name: Optional[str] = None,
    description: str = "",
    category: str = "general",
    requires_auth: bool = True,
    rate_limited: bool = True
):
    """
    Decorator to register a function as a tool with FastMCP.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description
        category: Tool category for organization
        requires_auth: Whether the tool requires authentication
        rate_limited: Whether the tool is rate-limited
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        # Set function attributes
        func._is_tool = True
        func._tool_name = name or func.__name__
        func._tool_description = description or func.__doc__ or ""
        func._tool_category = category
        func._requires_auth = requires_auth
        func._rate_limited = rate_limited
        
        # Apply standard decorators
        wrapped = handle_errors(log_execution(func))
        
        # Return the wrapped function with original attributes
        wrapped.__name__ = func.__name__
        wrapped.__doc__ = func.__doc__
        wrapped.__module__ = func.__module__
        
        return cast(F, wrapped)
    
    return decorator

@contextmanager
def timer(operation: str):
    """
    Context manager to time a block of code.
    
    Args:
        operation: Description of the operation being timed
    """
    start_time = time.time()
    logger.debug(f"Starting {operation}")
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.debug(f"Completed {operation} in {duration:.2f} seconds")

def validate_window_handle(handle: int) -> bool:
    """
    Validate if a window handle is valid.
    
    Args:
        handle: Window handle to validate
        
    Returns:
        bool: True if the handle is valid, False otherwise
    """
    from pywinauto import Desktop
    
    try:
        window = Desktop(backend="uia").window(handle=handle)
        return window.exists()
    except Exception:
        return False

def get_desktop():
    """Get a Desktop instance with proper error handling."""
    from pywinauto import Desktop
    
    try:
        return Desktop(backend="uia")
    except Exception as e:
        logger.error(f"Failed to initialize Desktop: {e}", exc_info=True)
        raise RuntimeError("Failed to initialize Windows Desktop automation") from e
