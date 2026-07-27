from fastapi import APIRouter, File, UploadFile, status, BackgroundTasks
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService
from app.services.scan_status_service import ScanStatusService

router = APIRouter()

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_project(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload a project ZIP file.
    Max size: 100MB.
    """
    return await UploadService.process_upload(file, background_tasks)

@router.get("/scan/status/{project_id}")
async def get_scan_status(project_id: str):
    """
    Returns the current status of a background scan.
    """
    return {"status": ScanStatusService.get_status(project_id)}
