import uuid
import logging
from fastapi import APIRouter, status, Depends, UploadFile, File

from app.schemas.scan_schema import ScanResponse
from app.services.certificate_parsing_service import CertificateParsingService
from app.services.asset_graph_ingestion_service import AssetGraphIngestionService
from app.services.scan_status_service import ScanStatusService, ScanStage
from app.core.security import get_current_user_strict, User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def upload_certificate(
    file: UploadFile = File(...), user: User = Depends(get_current_user_strict)
):
    """
    Parse an uploaded certificate (.pem/.crt) and ingest the cryptographic assets into the graph.
    """
    project_id = str(uuid.uuid4())
    
    try:
        ScanStatusService.set_status(project_id, ScanStage.SCANNING)
        content = await file.read()
        
        parsed_cert = CertificateParsingService.parse_certificate_bytes(content)
        parsed_cert['source'] = file.filename
        
        ScanStatusService.set_status(project_id, ScanStage.BUILDING_GRAPH)
        AssetGraphIngestionService.ingest_certificates(
            project_id=project_id, 
            parsed_certs=[parsed_cert],
            user_id=user.id,
            owner_email=user.email
        )
        ScanStatusService.set_status(project_id, ScanStage.COMPLETED)
        
        return ScanResponse(
            project_id=project_id,
            status="completed",
            message=f"Successfully scanned {file.filename}",
        )
    except Exception as e:
        logger.error(f"Certificate scan failed: {e}")
        ScanStatusService.set_status(project_id, ScanStage.FAILED)
        return ScanResponse(project_id=project_id, status="failed", message=str(e))
