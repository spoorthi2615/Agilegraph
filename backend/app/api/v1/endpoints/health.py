from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from typing import Optional
from neo4j import GraphDatabase

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health")

class LivenessResponse(BaseModel):
    status: str

class ReadinessResponse(BaseModel):
    status: str
    database: str
    service: str
    version: str
    reason: Optional[str] = None

@router.get("/live", response_model=LivenessResponse)
def liveness_check() -> LivenessResponse:
    """
    Liveness check endpoint.
    Answers: Is the FastAPI process alive? (No database required)
    """
    return LivenessResponse(status="alive")


import spaces

@router.get("/ready", response_model=ReadinessResponse)
@spaces.GPU
def readiness_check(response: Response) -> ReadinessResponse:
    """
    Readiness check endpoint.
    Answers: Can AgileGraph actually function? (Verifies DB connectivity)
    """
    try:
        # Initialize a lightweight driver just to verify connectivity
        with GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        ) as driver:
            driver.verify_connectivity()
            
        return ReadinessResponse(
            status="ready",
            database="connected",
            service=settings.APP_NAME,
            version=settings.VERSION
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        # Return 503 Service Unavailable if the database is unreachable
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="not_ready",
            database="unreachable",
            service=settings.APP_NAME,
            version=settings.VERSION,
            reason="Unable to connect to Neo4j"
        )
