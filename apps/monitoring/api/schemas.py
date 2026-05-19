from drf_spectacular.utils import (OpenApiExample, OpenApiResponse,
                                   OpenApiTypes, extend_schema)

health_schema = extend_schema(
    tags=["Monitoring"],
    summary="Health Check",
    description="Check if the application is healthy.",
    responses={
        200: OpenApiResponse(
            description="OK",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    "Success",
                    value={"status": "ok", "database": "ok"},
                ),
            ],
        ),
        400: dict,
    },
)
readiness_schema = extend_schema(
    tags=["Monitoring"],
    summary="Readiness Check",
    description="Check if the application is ready to serve requests.",
    responses={
        200: OpenApiResponse(
            description="OK",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    "Success",
                    value={
                        "status": "ready",
                        "details": {"database": "ok", "redis": "ok"},
                    },
                ),
            ],
        ),
    },
)
