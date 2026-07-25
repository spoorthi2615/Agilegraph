from pydantic import BaseModel

class UploadResponse(BaseModel):
    project_id: str
    filename: str
    status: str
