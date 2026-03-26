from django.urls import path

from apps.monitoring.api.views import HealthView, ReadinessView

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("ready", ReadinessView.as_view(), name="readiness"),
]
