from . import test as test_settings

# Re-export uppercase settings from the test module for CI inheritance.
for setting_name in dir(test_settings):
    if setting_name.isupper():
        globals()[setting_name] = getattr(test_settings, setting_name)

SECRET_KEY = (
    "ci-only-secret-key-for-deploy-checks-please-replace-with-a-real-secret-key"
)
SECURE_SSL_REDIRECT = True
