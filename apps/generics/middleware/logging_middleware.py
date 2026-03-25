# app/core/middleware/logging_middleware.py
import uuid
import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("app")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming requests, response status, and request duration.
    Adds a correlation ID to each request.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.correlation_id = request_id

        # Log incoming request
        logger.info(
            json.dumps(
                {
                    "event": "request_started",
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host,
                    "request_id": request_id,
                }
            )
        )

        import time

        start = time.time()
        response = await call_next(request)
        process_time = (time.time() - start) * 1000  # ms

        # Add correlation ID to response header
        response.headers["X-Request-ID"] = request_id

        # Log completed request
        logger.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time, 2),
                    "client_ip": request.client.host,
                    "request_id": request_id,
                }
            )
        )

        return response
