from rest_framework.response import Response


def api_response(
    data=None, message: str = "", success: bool = True, status_code: int = 200
):
    """
    Standard API response format.
    """
    return Response(
        {
            "success": success,
            "message": message,
            "data": data if data is not None else {},
        },
        status=status_code,
    )
