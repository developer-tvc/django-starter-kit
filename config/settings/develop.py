from . import base as base_settings

# Re-export uppercase settings from the base module for local development.
for setting_name in dir(base_settings):
    if setting_name.isupper():
        globals()[setting_name] = getattr(base_settings, setting_name)

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# CORS Configurations
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:4200", "http://localhost:4200"]

CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:4200", "http://localhost:4200"]
