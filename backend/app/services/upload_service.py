import os
import uuid
import shutil
from fastapi import UploadFile
from app.core.exceptions import ValidationException, EntityTooLargeException, AgileGraphException
from app.config.settings import settings
from app.schemas.upload_schema import UploadResponse

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

class UploadService:
    @staticmethod
    async def process_upload(file: UploadFile) -> UploadResponse:
        # Sanitize filename to prevent path traversal
        original_name = file.filename or ""
        # Handle both Windows and Unix path separators sent by clients
        normalized_name = original_name.replace("\\", "/")
        safe_filename = os.path.basename(normalized_name)
        
        # Ensure the filename is not empty or inherently malicious like "." or ".."
        if not safe_filename or safe_filename in {".", ".."}:
            raise ValidationException("Invalid filename provided.")

        # Validate extension using the sanitized name
        if not safe_filename.lower().endswith('.zip'):
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
        # Default fallback to "uploads" if not set
        base_upload_dir = settings.UPLOAD_DIRECTORY or "uploads"
        # Since we run from backend root, base_upload_dir is 'uploads'
        project_dir = os.path.join(base_upload_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        file_path = os.path.join(project_dir, safe_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise AgileGraphException(f"Failed to save file: {str(e)}")
        finally:
            file.file.close()
            
        return UploadResponse(
            project_id=project_id,
            filename=safe_filename,
            status="uploaded"
        )
