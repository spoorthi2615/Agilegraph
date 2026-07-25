from fastapi import APIRouter, File, UploadFile, status
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter()

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_project(file: UploadFile = File(...)):
    """
    Upload a project ZIP file.
    Max size: 100MB.
    """
    return await UploadService.process_upload(file)
