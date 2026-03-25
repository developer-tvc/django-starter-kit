# apps/generics/utils/json_formatter.py
import logging
import json
from datetime import datetime
import threading


class CustomJSONFormatter(logging.Formatter):
    """
    Formats log records as JSON with timestamp, level, module, and message.
    """

    def format(self, record):
        current_user = getattr(threading.current_thread(), "_django_user", None)
        user_id = getattr(current_user, "id", None) if current_user else None
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "correlation_id": getattr(record, "correlation_id", None),
            "user_id": user_id,
            "duration_ms": getattr(
                threading.current_thread(), "_request_duration_ms", None
            ),
        }

        # Include extra fields if present
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id

        return json.dumps(log_record)
