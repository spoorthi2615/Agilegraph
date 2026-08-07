from typing import List

from fastapi import APIRouter, Depends

from app.core.security import User, get_current_user_strict
from app.models.topbar import Workspace

router = APIRouter()


@router.get("/all", response_model=List[Workspace])
def get_workspaces(user: User = Depends(get_current_user_strict)) -> List[Workspace]:
    return [
        Workspace(id="ws-1", name="Acme Bank", environment="PROD", is_active=True),
        Workspace(id="ws-2", name="Acme Bank", environment="STAGING", is_active=False),
        Workspace(id="ws-3", name="Global HQ", environment="DEV", is_active=False),
    ]
