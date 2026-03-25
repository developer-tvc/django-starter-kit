# apps/generics/middleware/correlation_id_middleware.py
import threading
import uuid
import time
import logging

logger = logging.getLogger("apps")  # your app logger
_thread_locals = threading.local()


def get_current_correlation_id():
    return getattr(_thread_locals, "correlation_id", None)


class CorrelationIdMiddleware:
    """
    Assigns a correlation ID to each request, stores it in thread-local,
    and optionally logs request start/end with duration.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Get existing ID or generate new
        correlation_id = request.META.get("HTTP_X_CORRELATION_ID", str(uuid.uuid4()))
        request.correlation_id = correlation_id
        _thread_locals.correlation_id = correlation_id

        # User ID if authenticated
        user_id = (
            getattr(request.user, "id", None) if hasattr(request, "user") else None
        )

        # Log request start
        logger.info(
            "request_started",
            extra={
                "method": request.method,
                "path": request.get_full_path(),
                "correlation_id": correlation_id,
                "user_id": user_id,
            },
        )

        try:
            response = self.get_response(request)
        except Exception as e:
            logger.exception(
                "unhandled_exception",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                },
            )
            raise

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        response["X-Correlation-ID"] = correlation_id
        # Store duration in thread for logging
        threading.current_thread()._request_duration_ms = duration_ms
        # Log request completed
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.get_full_path(),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": correlation_id,
                "user_id": user_id,
            },
        )

        return response
