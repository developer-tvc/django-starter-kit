import logging
import traceback
from datetime import UTC, datetime

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("apps")


class GlobalExceptionMiddleware(MiddlewareMixin):
    """
    Catch all unhandled exceptions globally,
    log them in JSON format, and return a structured JSON response.
    """

    def process_exception(self, request, exception):
        # Log exception details
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": "ERROR",
            "message": str(exception),
            "module": exception.__class__.__name__,
            "path": request.path,
            "method": request.method,
            "stack_trace": traceback.format_exc(),
        }

        # Include user info if available
        if hasattr(request, "user") and request.user.is_authenticated:
            log_data["user_id"] = request.user.id

        logger.error(log_data)

        # Return JSON response
        response_data = {
            "detail": "An unexpected error occurred.",
        }
        return JsonResponse(response_data, status=500)
