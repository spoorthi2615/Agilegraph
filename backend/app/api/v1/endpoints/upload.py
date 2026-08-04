from fastapi import APIRouter, File, UploadFile, status, BackgroundTasks, Depends
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import UploadService
from app.services.scan_status_service import ScanStatusService
from app.core.security import get_current_user_strict, User

router = APIRouter()

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_project(background_tasks: BackgroundTasks, file: UploadFile = File(...), user: User = Depends(get_current_user_strict)):
    """
    Upload a project ZIP file.
    Max size: 100MB.
    """
    return await UploadService.process_upload(file, background_tasks, user_id=user.id, owner_email=user.email)

@router.get("/scan/status/{project_id}")
async def get_scan_status(project_id: str):
    """
    Returns the current status of a background scan.
    """
    return {"status": ScanStatusService.get_status(project_id)}
