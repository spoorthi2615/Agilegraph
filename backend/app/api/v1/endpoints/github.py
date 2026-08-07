from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.security import User, get_current_user_strict
from app.schemas.github_schema import GithubImportRequest, GithubImportResponse
from app.services.github_import_service import GitHubImportService

router = APIRouter()


@router.post("/github", response_model=GithubImportResponse, status_code=status.HTTP_201_CREATED)
async def import_github_repository(
    background_tasks: BackgroundTasks,
    request: GithubImportRequest,
    user: User = Depends(get_current_user_strict),
):
    """
    Import a project via GitHub repository URL.
    Does not clone or download the repository yet.
    """
    return await GitHubImportService.process_import(
        request, background_tasks, user_id=user.id, owner_email=user.email
    )
