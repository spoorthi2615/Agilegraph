from typing import Optional

import networkx as nx
from fastapi import APIRouter, Depends, Query
from fastapi import Path as PathParam

from app.config.settings import settings
from app.models.graph import (
    GraphEdge,
    GraphFilter,
    GraphMetadata,
    GraphNode,
    GraphResponse,
    GraphStatistics,
    NodeDetails,
)
from app.services.graph_query_service import GraphQueryService
from app.services.recommendation_workflow_service import RecommendationWorkflowService

router = APIRouter()


def get_graph_query_service() -> Optional[GraphQueryService]:
    if not settings.NEO4J_URI:
        yield None
        return

    try:
        service = GraphQueryService(
            uri=settings.NEO4J_URI, user=settings.NEO4J_USERNAME, password=settings.NEO4J_PASSWORD
        )
        yield service
    except Exception:
        yield None
    finally:
        try:
            if "service" in locals() and service is not None:
                service.close()
        except Exception:
            pass


def get_recommendation_workflow_service(
    query_service: Optional[GraphQueryService] = Depends(get_graph_query_service),
) -> RecommendationWorkflowService:
    return RecommendationWorkflowService(query_service=query_service)


@router.get("", response_model=GraphResponse)
def get_graph(
    repository: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    node_type: Optional[str] = Query(None),
    algorithm: Optional[str] = Query(None),
    pqc_status: Optional[str] = Query(None),
    query_service: Optional[GraphQueryService] = Depends(get_graph_query_service),
) -> GraphResponse:
    """
    Retrieves the visual graph data structure including nodes, edges, statistics, and metadata.
    Applies filtering natively.
    """
    # Empty State Policy: Default values if graph is empty or not fully populated
    filters = GraphFilter(
        repository=repository,
        risk_level=risk_level,
        severity=severity,
        node_type=node_type,
        algorithm=algorithm,
        pqc_status=pqc_status,
    )

    raw_nodes = []
    raw_edges = []
    if query_service:
        try:
            raw_graph = query_service.get_entire_graph()
            raw_nodes = raw_graph.get("nodes", [])
            raw_edges = raw_graph.get("edges", [])
        except Exception:
            raw_nodes = []
            raw_edges = []
        raw_nodes = []
        raw_edges = []

    nodes = []
    edges = []

    for raw in raw_nodes:
        asset_id = str(raw.get("node_id", "unknown"))
        nodes.append(
            GraphNode(
                id=asset_id,
                label=raw.get("label", "Unknown Asset"),
                type=str(raw.get("node_type", "service")).lower(),
                risk=str(raw.get("severity", "medium")).lower(),
                x=0.0,
                y=0.0,
            )
        )

    for edge in raw_edges:
        edges.append(GraphEdge(source=str(edge.get("source")), target=str(edge.get("target"))))

    # Apply layout so nodes don't stack at (0,0)
    if nodes:
        nx_graph = nx.Graph()
        for n in nodes:
            nx_graph.add_node(n.id)
        for e in edges:
            nx_graph.add_edge(e.source, e.target)

        try:
            pos = nx.spring_layout(nx_graph, k=0.15, iterations=50, scale=450, center=(500, 320))
            for n in nodes:
                if n.id in pos:
                    n.x = float(pos[n.id][0])
                    n.y = float(pos[n.id][1])
        except Exception:
            pass

    stats = GraphStatistics(
        total_nodes=len(nodes),
        total_edges=len(edges),
        connected_components=1 if nodes else 0,
        critical_assets=len([n for n in nodes if n.risk == "critical"]),
        high_risk_assets=len([n for n in nodes if n.risk == "high"]),
        pqc_ready_assets=0,
        average_degree=0.0,
        graph_density=0.0,
    )

    metadata = GraphMetadata(
        repository_name=repository or "AgileGraph", graph_size=f"{len(nodes) * 2} KB"
    )

    return GraphResponse(
        nodes=nodes, edges=edges, statistics=stats, metadata=metadata, filters=filters
    )


@router.get("/node/{node_id}", response_model=NodeDetails)
def get_node_detail(
    node_id: str = PathParam(...),
    query_service: Optional[GraphQueryService] = Depends(get_graph_query_service),
    rec_workflow: RecommendationWorkflowService = Depends(get_recommendation_workflow_service),
) -> NodeDetails:
    """
    Retrieves complete details for a single graph node required for the side panel.
    """
    node_data = None
    if query_service:
        try:
            node_data = query_service.get_node_by_id(node_id)
        except Exception:
            node_data = None

    if not node_data:
        # Return a fallback empty object if node isn't found
        return NodeDetails(
            id=node_id,
            name="Unknown",
            type="unknown",
            department="N/A",
            algorithm="N/A",
            key_size="N/A",
            risk_score=0,
            risk="low",
            status="not-started",
            priority=0,
            location="N/A",
            description="Node not found.",
            connected_assets=[],
            incoming_relationships=[],
            outgoing_relationships=[],
            certificates=[],
            dependencies=[],
            explainability_summary={},
            migration_recommendation={},
            graph_metrics={},
        )

    return NodeDetails(
        id=node_id,
        name=node_data.get("label", "Node Details"),
        type=node_data.get("node_type", "service"),
        department="Engineering",
        algorithm=node_data.get("algorithm", "N/A"),
        key_size=str(node_data.get("key_size", "N/A")),
        risk_score=node_data.get("risk_score", 0),
        risk=str(node_data.get("severity", "medium")).lower(),
        status="not-started",
        priority=node_data.get("risk_score", 0),
        location=node_data.get("file_path", "N/A"),
        description=f"Detailed view of {node_data.get('label', 'asset')}.",
        connected_assets=[],
        incoming_relationships=[],
        outgoing_relationships=[],
        certificates=[],
        dependencies=[],
        explainability_summary={},
        migration_recommendation={},
        graph_metrics={},
    )
