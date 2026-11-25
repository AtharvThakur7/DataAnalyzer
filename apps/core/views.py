from django.http import JsonResponse
from django.db import connection


def health_check(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    healthy = db_ok
    return JsonResponse(
        {'status': 'healthy' if healthy else 'unhealthy', 'database': db_ok},
        status=200 if healthy else 503,
    )
