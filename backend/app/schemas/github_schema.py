from pydantic import BaseModel
from typing import Optional

class GithubImportRequest(BaseModel):
    repository_url: str
    access_token: Optional[str] = None
    branch: Optional[str] = None

class GithubImportResponse(BaseModel):
    project_id: str
    repository_url: str
    status: str
