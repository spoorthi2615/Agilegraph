from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Any

from app.config.settings import settings
from app.services.project_analysis_service import ProjectAnalysisService
from app.services.risk_scoring_service import RiskScoringService
from app.services.graph_query_service import GraphQueryService
from app.services.analysis_workflow_service import AnalysisWorkflowService
from app.scanners.scanner_registry import get_default_registry

router = APIRouter()

# ---------------------------------------------------------
# Dependency Injection Providers
# ---------------------------------------------------------

def get_project_analysis_service() -> ProjectAnalysisService:
    registry = get_default_registry()
    return ProjectAnalysisService(registry=registry)

def get_neo4j_export_service() -> Neo4jExportService:
    from app.services.neo4j_export_service import Neo4jExportService
    return Neo4jExportService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )

def get_analysis_workflow_service(
    analysis_service: ProjectAnalysisService = Depends(get_project_analysis_service),
    export_service = Depends(get_neo4j_export_service)
) -> AnalysisWorkflowService:
    return AnalysisWorkflowService(
        analysis_service=analysis_service,
        export_service=export_service
    )

def get_graph_query_service() -> GraphQueryService:
    return GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class AnalysisRequest(BaseModel):
    project_id: str
    project_path: str

# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@router.post("")
def run_analysis(
    request: AnalysisRequest,
    workflow_service: AnalysisWorkflowService = Depends(get_analysis_workflow_service)
) -> Dict[str, Any]:
    """
    Orchestrates the static analysis pipeline, applies risk scoring, builds the graph,
    and exports it to Neo4j.
    """
    project_path = Path(request.project_path)
    if not project_path.exists() or not project_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid or missing project directory")
        
    try:
        result = workflow_service.execute_pipeline(request.project_id, project_path)
        
        return {
            "status": result["status"],
            "project_id": request.project_id,
            "metrics": {
                "total_findings": result["total_findings"],
                "node_count": result["node_count"],
                "edge_count": result["edge_count"]
            },
            "message": "Graph successfully built and exported to Neo4j."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/high-risk")
def get_high_risk(query_service: GraphQueryService = Depends(get_graph_query_service)) -> Dict[str, Any]:
    """
    Retrieves all cryptographic assets possessing a critical risk score.
    """
    try:
        results = query_service.get_high_risk_assets()
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        query_service.close()


@router.get("/summary")
def get_summary(query_service: GraphQueryService = Depends(get_graph_query_service)) -> Dict[str, Any]:
    """
    Retrieves global statistics for the currently exported graph.
    """
    try:
        results = query_service.get_summary_statistics()
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        query_service.close()


@router.get("/file")
def get_file_assets(
    file_path: str = Query(..., description="The absolute path to the file"),
    query_service: GraphQueryService = Depends(get_graph_query_service)
) -> Dict[str, Any]:
    """
    Retrieves all cryptographic assets physically located within the specified file.
    """
    try:
        results = query_service.get_assets_in_file(file_path)
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        query_service.close()


@router.get("/dependency")
def get_dependency_files(
    package_name: str = Query(..., description="The name of the software dependency"),
    query_service: GraphQueryService = Depends(get_graph_query_service)
) -> Dict[str, Any]:
    """
    Retrieves all source code files that import or utilize the specified dependency.
    """
    try:
        results = query_service.get_files_using_dependency(package_name)
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        query_service.close()
