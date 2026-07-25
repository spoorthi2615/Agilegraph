import os
import zipfile
import stat
from fastapi import HTTPException, status
from app.config.settings import settings

MAX_EXTRACTED_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_CUMULATIVE_EXTRACTED_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_FILES_IN_ARCHIVE = 10000

class ProjectExtractionService:
    @staticmethod
    def extract_project(project_id: str) -> dict:
        """
        Safely extracts an uploaded ZIP file for a given project_id.
        """
        base_upload_dir = settings.UPLOAD_DIRECTORY or "uploads"
        project_dir = os.path.join(base_upload_dir, project_id)
        
        if not os.path.exists(project_dir):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project directory not found for ID: {project_id}"
            )
            
        # Locate the uploaded ZIP file inside the project directory
        zip_path = None
        for file in os.listdir(project_dir):
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(project_dir, file)
                break
                
        if not zip_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No ZIP file found in the project directory."
            )
            
        source_dir = os.path.join(project_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        resolved_source_dir = os.path.abspath(source_dir)
        
        extracted_files_count = 0
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                infolist = zip_ref.infolist()
                
                # 5. Reject archives containing more than 10,000 files
                if len(infolist) > MAX_FILES_IN_ARCHIVE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Archive contains too many files (max {MAX_FILES_IN_ARCHIVE})."
                    )
                
                cumulative_size = 0
                
                for zinfo in infolist:
                    # 3. Reject absolute paths
                    if zinfo.filename.startswith('/') or zinfo.filename.startswith('\\'):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Archive contains absolute paths which are not allowed."
                        )
                        
                    # 1. Prevent ZIP Slip (Directory Traversal)
                    resolved_target_path = os.path.abspath(os.path.join(resolved_source_dir, zinfo.filename))
                    
                    # Target path must be strictly inside the source directory.
                    # We check if it starts with the directory path + OS separator,
                    # or if the entry is exactly the source directory itself (e.g., zip contains root folder).
                    if not resolved_target_path.startswith(resolved_source_dir + os.sep) and resolved_target_path != resolved_source_dir:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Archive attempts directory traversal (ZIP Slip)."
                        )
                        
                    # 2. Reject symbolic links
                    # Unix symlink attributes are stored in the upper 16 bits
                    mode = zinfo.external_attr >> 16
                    if mode and stat.S_ISLNK(mode):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Archive contains symbolic links which are not allowed."
                        )
                        
                    # 4. Reject entries larger than 100 MB after extraction
                    if zinfo.file_size > MAX_EXTRACTED_FILE_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Archive contains an uncompressed file exceeding the {MAX_EXTRACTED_FILE_SIZE // (1024*1024)}MB limit."
                        )
                        
                    # 5. Reject archives exceeding 500 MB cumulative extracted size
                    cumulative_size += zinfo.file_size
                    if cumulative_size > MAX_CUMULATIVE_EXTRACTED_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Archive exceeds the maximum cumulative extracted size of {MAX_CUMULATIVE_EXTRACTED_SIZE // (1024*1024)}MB."
                        )

                # All validations passed safely; proceed with extraction
                zip_ref.extractall(source_dir)
                extracted_files_count = len(infolist)
                
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid ZIP archive."
            )
        except HTTPException:
            # Re-raise known HTTP exceptions explicitly so they aren't masked
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to safely extract project: {str(e)}"
            )
            
        return {
            "project_id": project_id,
            "status": "extracted",
            "extracted_files_count": extracted_files_count,
            "source_directory": source_dir
        }
