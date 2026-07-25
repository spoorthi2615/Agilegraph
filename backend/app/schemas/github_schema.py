from pydantic import BaseModel

class GithubImportRequest(BaseModel):
    repository_url: str

class GithubImportResponse(BaseModel):
    project_id: str
    repository_url: str
    status: str
