import time

from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter()

# Simple runtime stats
START_TIME = time.time()
metrics_store = {"requests_total": 0, "errors_total": 0, "successful_requests": 0}


@router.get("/metrics", response_model=dict)
def get_metrics() -> dict:
    """
    Returns lightweight operational metrics for monitoring.
    """
    uptime = time.time() - START_TIME

    return {
        "uptime_seconds": int(uptime),
        "requests_total": metrics_store["requests_total"],
        "errors_total": metrics_store["errors_total"],
        "successful_requests": metrics_store["successful_requests"],
        "application_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


def increment_request_metrics(status_code: int):
    """Helper to be called by middleware to update metrics"""
    metrics_store["requests_total"] += 1
    if 200 <= status_code < 400:
        metrics_store["successful_requests"] += 1
    else:
        metrics_store["errors_total"] += 1
