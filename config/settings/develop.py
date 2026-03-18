from .base import *

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost"
]

# CORS Configurations
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:4200",
    "http://localhost:4200"
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:4200",
    "http://localhost:4200"
]
