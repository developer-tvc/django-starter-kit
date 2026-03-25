import logging


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        # Import lazily to avoid AppRegistryNotReady at startup
        from apps.generics.middleware.current_user_middleware import get_current_user
        from apps.generics.middleware.correlation_id_middleware import (
            get_current_correlation_id,
        )

        user = get_current_user()
        record.user_id = getattr(user, "user", None)
        record.correlation_id = get_current_correlation_id()
        return True
