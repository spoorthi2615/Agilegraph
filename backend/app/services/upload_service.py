import os
import shutil
import uuid

from fastapi import BackgroundTasks, UploadFile

from app.config.settings import settings
from app.core.exceptions import (
    AgileGraphException,
    EntityTooLargeException,
    ValidationException,
)
from app.schemas.upload_schema import UploadResponse
from app.services.scan_status_service import ScanStage, ScanStatusService

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


class UploadService:
    @staticmethod
    async def process_upload(
        file: UploadFile,
        background_tasks: BackgroundTasks,
        user_id: str = None,
        owner_email: str = None,
    ) -> UploadResponse:
        # Sanitize filename to prevent path traversal
        original_name = file.filename or ""
        # Handle both Windows and Unix path separators sent by clients
        normalized_name = original_name.replace("\\", "/")
        safe_filename = os.path.basename(normalized_name)

        # Ensure the filename is not empty or inherently malicious like "." or ".."
        if not safe_filename or safe_filename in {".", ".."}:
            raise ValidationException("Invalid filename provided.")

        # Validate extension using the sanitized name
        if not safe_filename.lower().endswith(".zip"):
            raise ValidationException("Only .zip files are allowed.")

        # Validate size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise EntityTooLargeException("File size exceeds the 100 MB limit.")

        # Generate unique project ID
        project_id = str(uuid.uuid4())

        # Ensure uploads directory and project folder exist
        base_upload_dir = settings.UPLOAD_DIRECTORY or "uploads"
        project_dir = os.path.join(base_upload_dir, project_id)
        extracted_dir = os.path.join(project_dir, "extracted")
        os.makedirs(extracted_dir, exist_ok=True)

        file_path = os.path.join(project_dir, safe_filename)

        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise AgileGraphException(f"Failed to save file: {str(e)}")
        finally:
            file.file.close()

        # Unzip safely
        import zipfile

        try:
            ScanStatusService.set_status(project_id, ScanStage.EXTRACTING)
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                # Sanitize extracted paths
                for member in zip_ref.namelist():
                    member_path = os.path.normpath(member)
                    # Check for zip slip and absolute paths on both Unix and Windows
                    if (
                        member_path.startswith("..") 
                        or member_path.startswith("/") 
                        or member_path.startswith("\\")
                        or (len(member_path) > 1 and member_path[1] == ":")
                    ):
                        raise ValidationException(f"Zip slip detected in path: {member}")
                zip_ref.extractall(extracted_dir)
        except zipfile.BadZipFile:
            ScanStatusService.set_status(project_id, ScanStage.FAILED)
            raise ValidationException("Uploaded file is not a valid ZIP archive.")
        except Exception as e:
            ScanStatusService.set_status(project_id, ScanStage.FAILED)
            if isinstance(e, ValidationException):
                raise e
            raise AgileGraphException(f"Failed to extract ZIP file: {str(e)}")

        # Execute pipeline in background
        from pathlib import Path

        from app.scanners.scanner_registry import get_default_registry
        from app.services.analysis_workflow_service import AnalysisWorkflowService
        from app.services.neo4j_export_service import Neo4jExportService
        from app.services.project_analysis_service import ProjectAnalysisService

        analysis_service = ProjectAnalysisService(get_default_registry())
        export_service = Neo4jExportService(
            settings.NEO4J_URI, settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD
        )
        workflow = AnalysisWorkflowService(analysis_service, export_service)

        ScanStatusService.set_status(project_id, ScanStage.QUEUED)
        background_tasks.add_task(
            workflow.execute_pipeline,
            project_id,
            Path(extracted_dir),
            user_id,
            owner_email,
        )

        return UploadResponse(project_id=project_id, filename=safe_filename, status="queued")
