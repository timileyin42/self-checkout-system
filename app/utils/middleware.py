import time
from fastapi import Request
from typing import Callable
from uuid import uuid4
from app.utils.logger import get_logger, RequestIdFilter, log_extra

logger = get_logger("middleware")

async def request_middleware(request: Request, call_next: Callable):
    """Middleware for request processing"""
    request_id = str(uuid4())
    request.state.request_id = request_id
    
    # Add request ID to logs
    for handler in logger.handlers:
        handler.addFilter(RequestIdFilter(request_id))
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(
            "Request failed",
            extra=log_extra(
                error=str(exc),
                request_method=request.method,
                request_path=request.url.path
            )
        )
        raise exc
    
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    response.headers["X-Request-ID"] = request_id
    
    logger.info(
        "Request completed",
        extra=log_extra(
            request_method=request.method,
            request_path=request.url.path,
            status_code=response.status_code,
            process_time=process_time
        )
    )
    
    return response
