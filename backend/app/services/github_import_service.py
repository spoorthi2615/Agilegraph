import uuid
import re
import os
import shutil
import subprocess
from pathlib import Path
import logging

from app.schemas.github_schema import GithubImportRequest, GithubImportResponse
from app.core.exceptions import ValidationException, AgileGraphException
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GitHubImportService:
    @staticmethod
    async def process_import(request: GithubImportRequest) -> GithubImportResponse:
        url = request.repository_url.strip()
        
        # Regex to validate the URL format strictly matches a GitHub repository
        github_pattern = re.compile(
            r'^https?://(www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?(\.git)?$'
        )
        
        match = github_pattern.match(url)
        if not match:
            raise ValidationException("Invalid GitHub repository URL provided. Must be a valid github.com repository.")
            
        # Optional: insert access token if provided
        clone_url = url
        if request.access_token:
            # We assume it's https
            if url.startswith("https://"):
                clone_url = url.replace("https://", f"https://{request.access_token}@")
            elif url.startswith("http://"):
                clone_url = url.replace("http://", f"http://{request.access_token}@")
                
        project_id = str(uuid.uuid4())
        
        base_upload_dir = settings.UPLOAD_DIRECTORY or "uploads"
        project_dir = os.path.join(base_upload_dir, project_id)
        clone_dir = os.path.join(project_dir, "extracted")
        os.makedirs(project_dir, exist_ok=True)
        
        # Execute git clone
        clone_cmd = ["git", "clone", "--depth=1"]
        if request.branch:
            clone_cmd.extend(["--branch", request.branch])
        clone_cmd.extend([clone_url, clone_dir])
        
        try:
            # Clone repo
            process = subprocess.run(
                clone_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                timeout=60,
                text=True
            )
            
            if process.returncode != 0:
                # Sanitize the error message to remove token if present
                err_msg = process.stderr
                if request.access_token:
                    err_msg = err_msg.replace(request.access_token, "***")
                logger.error(f"Git clone failed: {err_msg}")
                raise AgileGraphException(f"Failed to clone repository: Git error.")
                
            # Execute pipeline
            from app.services.analysis_workflow_service import AnalysisWorkflowService
            from app.services.project_analysis_service import ProjectAnalysisService
            from app.services.neo4j_export_service import Neo4jExportService
            from app.scanners.registry import get_default_registry
            
            analysis_service = ProjectAnalysisService(get_default_registry())
            export_service = Neo4jExportService(settings.NEO4J_URI, settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            
            workflow = AnalysisWorkflowService(analysis_service, export_service)
            pipeline_result = workflow.execute_pipeline(project_id, Path(clone_dir))
            
            return GithubImportResponse(
                project_id=project_id,
                repository_url=url,
                status="imported_and_processed"
            )
            
        except subprocess.TimeoutExpired:
            logger.error(f"Git clone timed out for {url}")
            raise AgileGraphException("Repository clone timed out after 60 seconds.")
        except Exception as e:
            logger.error(f"Pipeline execution failed for {project_id}: {str(e)}")
            raise AgileGraphException(f"Pipeline execution failed: {str(e)}")
        finally:
            # Clean up the temp clone directory regardless of success/failure
            if os.path.exists(clone_dir):
                shutil.rmtree(clone_dir, ignore_errors=True)
                
