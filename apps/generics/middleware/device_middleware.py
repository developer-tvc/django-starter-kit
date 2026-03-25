import uuid


class DeviceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        device_id = request.headers.get("X-Device-ID")

        if not device_id:
            device_id = str(uuid.uuid4())

        request.device_id = device_id
        request.user_agent = request.META.get("HTTP_USER_AGENT")
        request.ip_address = self.get_client_ip(request)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
