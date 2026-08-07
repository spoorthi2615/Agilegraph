from typing import List

from fastapi import APIRouter

from app.models.topbar import Workspace

router = APIRouter()


@router.get("/all", response_model=List[Workspace])
def get_workspaces() -> List[Workspace]:
    return [
        Workspace(id="ws-1", name="Acme Bank", environment="PROD", is_active=True),
        Workspace(id="ws-2", name="Acme Bank", environment="STAGING", is_active=False),
        Workspace(id="ws-3", name="Global HQ", environment="DEV", is_active=False),
    ]
