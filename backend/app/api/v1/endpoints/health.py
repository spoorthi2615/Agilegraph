from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter()

@router.get("/health", response_model=dict)
def health_check() -> dict:
    """
    Health check endpoint to monitor application status.
    Returns the current status, service name, and version.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }
