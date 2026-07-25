from fastapi import APIRouter, status
from app.schemas.github_schema import GithubImportRequest, GithubImportResponse
from app.services.github_import_service import GitHubImportService

router = APIRouter()

@router.post("/github", response_model=GithubImportResponse, status_code=status.HTTP_201_CREATED)
async def import_github_repository(request: GithubImportRequest):
    """
    Import a project via GitHub repository URL.
    Does not clone or download the repository yet.
    """
    return await GitHubImportService.process_import(request)
