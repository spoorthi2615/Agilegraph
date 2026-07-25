import uuid
import re
from fastapi import HTTPException, status
from app.schemas.github_schema import GithubImportRequest, GithubImportResponse

class GitHubImportService:
    @staticmethod
    async def process_import(request: GithubImportRequest) -> GithubImportResponse:
        url = request.repository_url.strip()
        
        # Regex to validate the URL format strictly matches a GitHub repository
        # Valid: https://github.com/user/repo, http://github.com/user/repo.git
        github_pattern = re.compile(
            r'^https?://(www\.)?github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?(\.git)?$'
        )
        
        if not github_pattern.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitHub repository URL provided. Must be a valid github.com repository."
            )
            
        project_id = str(uuid.uuid4())
        
        # Cloning and downloading logic is intentionally omitted for Sprint 3.
        
        return GithubImportResponse(
            project_id=project_id,
            repository_url=url,
            status="validated"
        )
