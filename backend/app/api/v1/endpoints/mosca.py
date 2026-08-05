from fastapi import APIRouter, Query
from app.services.mosca_service import MoscaService

router = APIRouter(prefix="/mosca", tags=["mosca"])

@router.get("/calculate")
def calculate_mosca_index(
    x: int = Query(
        ..., description="Security shelf-life (years data must remain secure)"
    ),
    y: int = Query(..., description="Migration time (years required to transition)"),
    z: int = Query(..., description="Threat horizon (years until Q-Day)"),
):
    """
    Calculate the Mosca Readiness Index given x, y, and z parameters.
    """
    return MoscaService.calculate_index(x, y, z)
