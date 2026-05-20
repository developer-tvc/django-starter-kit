import redis
from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView

from apps.monitoring.api.schemas import health_schema, readiness_schema


@health_schema
class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            db_status = "ok"
        except Exception:
            db_status = "error"
        return JsonResponse(
            {"status": "ok" if db_status == "ok" else "error", "database": db_status}
        )


@readiness_schema
class ReadinessView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ready = True
        details = {}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            details["database"] = "ok"
        except Exception as e:
            details["database"] = f"error: {str(e)}"
            ready = False

        try:
            r = redis.Redis(host="localhost", port=6379)
            r.ping()
            details["redis"] = "ok"
        except Exception as e:
            details["redis"] = f"error: {str(e)}"
            ready = False

        return JsonResponse(
            {"status": "ready" if ready else "not ready", "details": details},
            status=200 if ready else 503,
        )
