from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler


class NotAllowedError(Exception):
    def __init__(self, message="You are not allowed to perform this operation."):
        self.message = message
        super().__init__(self.message)


class ExistsError(Exception):
    def __init__(self, message="This data already exists."):
        self.message = message
        super().__init__(self.message)


class NotExistsError(Exception):
    def __init__(self, message="This data does not exist."):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    def __init__(self, message="You are not allowed to perform this operation."):
        self.message = message
        super().__init__(self.message)


def custom_exception_handler(exc, context):
    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": "Too many requests. Please slow down."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return exception_handler(exc, context)
