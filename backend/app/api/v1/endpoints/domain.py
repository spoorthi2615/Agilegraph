import logging
import uuid

from fastapi import APIRouter, Depends, status

from app.core.security import User, get_current_user_strict
from app.schemas.scan_schema import DomainScanRequest, ScanResponse
from app.services.asset_graph_ingestion_service import AssetGraphIngestionService
from app.services.certificate_parsing_service import TLSScanningService
from app.services.scan_status_service import ScanStage, ScanStatusService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def scan_domain(request: DomainScanRequest, user: User = Depends(get_current_user_strict)):
    """
    Perform a TLS handshake against a domain, parse the certificate chain,
    and ingest the resulting cryptographic assets into the graph.
    """
    project_id = str(uuid.uuid4())

    try:
        ScanStatusService.set_status(project_id, ScanStage.SCANNING)
        parsed_certs = []
        for port in request.ports:
            certs = TLSScanningService.scan_domain(request.domain, port)
            parsed_certs.extend(certs)

        ScanStatusService.set_status(project_id, ScanStage.BUILDING_GRAPH)
        AssetGraphIngestionService.ingest_certificates(
            project_id=project_id,
            parsed_certs=parsed_certs,
            user_id=user.id,
            owner_email=user.email,
        )
        ScanStatusService.set_status(project_id, ScanStage.COMPLETED)

        return ScanResponse(
            project_id=project_id,
            status="completed",
            message=f"Successfully scanned {request.domain}",
        )
    except Exception as e:
        logger.error(f"Domain scan failed: {e}")
        ScanStatusService.set_status(project_id, ScanStage.FAILED)
        return ScanResponse(project_id=project_id, status="failed", message=str(e))
