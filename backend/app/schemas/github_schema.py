from typing import Optional

from pydantic import BaseModel


class GithubImportRequest(BaseModel):
    repository_url: str
    access_token: Optional[str] = None
    branch: Optional[str] = None


class GithubImportResponse(BaseModel):
    project_id: str
    repository_url: str
    status: str
