import os

os.environ.setdefault("ENV", "test")
os.environ.setdefault("PSQL_DB", "test_db")
os.environ.setdefault("PSQL_USER", "postgres")
os.environ.setdefault("PSQL_PASSWORD", "postgres")
os.environ.setdefault("PSQL_HOST", "localhost")
os.environ.setdefault("PSQL_PORT", "5432")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("LOGIN_LOCK_ENABLED", "False")
os.environ.setdefault("LOGIN_MAX_ATTEMPTS", "5")
os.environ.setdefault("LOGIN_LOCK_MINUTES", "15")
os.environ.setdefault("EMAIL_VERIFICATION_ENABLED", "False")
os.environ.setdefault("EMAIL_ENABLED", "False")
os.environ.setdefault("SMS_ENABLED", "False")
os.environ.setdefault("IN_APP_ENABLED", "True")
os.environ.setdefault("WEBHOOK_ENABLED", "False")

from .base import *  # noqa: F403,F401,E402

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
