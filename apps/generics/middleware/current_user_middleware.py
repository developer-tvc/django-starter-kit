# activity/middleware.py
import threading
from django.http import HttpRequest,JsonResponse
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, "user", None)


def get_user(request: HttpRequest):
    """
    Extract authenticated user from JWT.
    Returns:
      - user object if valid
      - None if no token
      - JsonResponse(401) if token is invalid/expired
    """
    try:
        user_token = JWTAuthentication().authenticate(request)
    except InvalidToken:
        return JsonResponse(
            {"detail": "Token is expired or invalid"},
            status=401
        )

    if user_token is None:
        return None

    user, _ = user_token

    if isinstance(user, AnonymousUser):
        return None

    return user

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = get_user(request)
        
        #Setting logged user in thread
        setattr(threading.current_thread(), '_django_user', user)
        
        _thread_locals.user = (
            request.user if request.user.is_authenticated else None
        )
        return self.get_response(request)
