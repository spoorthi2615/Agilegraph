import logging
import os
import re
import shutil
import subprocess
import uuid

from app.config.settings import settings
from app.core.exceptions import ValidationException
from app.schemas.github_schema import GithubImportRequest, GithubImportResponse

logger = logging.getLogger(__name__)

from fastapi import BackgroundTasks


class GitHubImportService:
    @staticmethod
    async def process_import(
        request: GithubImportRequest,
        background_tasks: BackgroundTasks,
        user_id: str = None,
        owner_email: str = None,
    ) -> GithubImportResponse:
        url = request.repository_url.strip()

        # Regex to validate the URL format strictly matches a GitHub repository
        github_pattern = re.compile(
            r"^https?://(www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?(\.git)?$"
        )

        match = github_pattern.match(url)
        if not match:
            raise ValidationException(
                "Invalid GitHub repository URL provided. Must be a valid github.com repository."
            )

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

        from app.services.scan_status_service import ScanStage, ScanStatusService

        ScanStatusService.set_status(project_id, ScanStage.QUEUED)

        # Schedule the blocking clone and analysis pipeline in the background
        background_tasks.add_task(
            GitHubImportService._run_pipeline_in_background,
            project_id,
            clone_url,
            request.branch,
            clone_dir,
            url,
            user_id,
            owner_email,
            request.access_token,
        )

        return GithubImportResponse(project_id=project_id, repository_url=url, status="queued")

    @staticmethod
    def _run_pipeline_in_background(
        project_id,
        clone_url,
        branch,
        clone_dir,
        original_url,
        user_id,
        owner_email,
        access_token,
    ):
        from app.services.scan_status_service import ScanStage, ScanStatusService

        ScanStatusService.set_status(project_id, ScanStage.CLONING)

        clone_cmd = ["git", "clone", "--depth=1"]
        if branch:
            clone_cmd.extend(["--branch", branch])
        clone_cmd.extend([clone_url, clone_dir])

        try:
            # Clone repo
            process = subprocess.run(
                clone_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
                text=True,
            )

            if process.returncode != 0:
                err_msg = process.stderr
                if access_token:
                    err_msg = err_msg.replace(access_token, "***")
                logger.error(f"Git clone failed: {err_msg}")
                ScanStatusService.set_status(project_id, ScanStage.FAILED)
                return

            # Execute pipeline
            from pathlib import Path

            from app.config.settings import settings
            from app.scanners.scanner_registry import get_default_registry
            from app.services.analysis_workflow_service import AnalysisWorkflowService
            from app.services.neo4j_export_service import Neo4jExportService
            from app.services.project_analysis_service import ProjectAnalysisService

            analysis_service = ProjectAnalysisService(get_default_registry())
            export_service = Neo4jExportService(
                settings.NEO4J_URI, settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD
            )

            workflow = AnalysisWorkflowService(analysis_service, export_service)
            workflow.execute_pipeline(
                project_id, Path(clone_dir), user_id=user_id, owner_email=owner_email
            )

        except subprocess.TimeoutExpired:
            logger.error(f"Git clone timed out for {original_url}")
            ScanStatusService.set_status(project_id, ScanStage.FAILED)
        except Exception as e:
            logger.error(f"Pipeline execution failed for {project_id}: {str(e)}")
            ScanStatusService.set_status(project_id, ScanStage.FAILED)
        finally:
            if os.path.exists(clone_dir):
                shutil.rmtree(clone_dir, ignore_errors=True)
