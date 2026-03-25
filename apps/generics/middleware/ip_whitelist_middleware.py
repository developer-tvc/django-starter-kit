from django.conf import settings
from django.http import JsonResponse
import logging
logger = logging.getLogger(__name__)

class IPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = getattr(settings, "IP_WHITELIST", [])

    def __call__(self, request):
        # Get client IP
        ip = self.get_client_ip(request)

        # Allow if no whitelist configured (fail-open for dev)
        if self.allowed_ips:
            if ip not in self.allowed_ips:
                logger.error(f"Access denied for IP: {ip}")
                return JsonResponse(
                    {"detail": "Access denied: IP not allowed"},
                    status=403
                )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # In case of proxy (nginx, load balancer)
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")