from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.config.settings import settings
from app.models.topbar import SearchResult
from app.services.graph_query_service import GraphQueryService


def get_query_service():
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


router = APIRouter()


@router.get("/all", response_model=List[SearchResult])
def search_graph(
    q: str = Query("", description="Search query"),
    query_service: Optional[GraphQueryService] = Depends(get_query_service),
) -> List[SearchResult]:
    if not q or len(q) < 2 or not query_service or not query_service.driver:
        return []

    # Simple Cypher query to find nodes matching the query in name, algorithm, or type
    cypher = """
    MATCH (n)
    WHERE toLower(n.label) CONTAINS toLower($q)
       OR toLower(n.algorithm) CONTAINS toLower($q)
       OR toLower(labels(n)[0]) CONTAINS toLower($q)
    RETURN n, labels(n)[0] AS label
    LIMIT 10
    """

    try:
        with query_service.driver.session() as session:
            result = session.run(cypher, q=q)
            results = []
        for record in result:
            node = record["n"]
            label = record["label"]

            # Map node to SearchResult based on label
            if label == "PROJECT":
                results.append(
                    SearchResult(
                        id=str(node.get("node_id", "unknown")),
                        title=node.get("label", "Unknown Project"),
                        type="scan",
                        subtitle="Project Repository",
                        url=f"/scan/{node.get('node_id', '')}",
                    )
                )
            elif label == "FILE":
                results.append(
                    SearchResult(
                        id=str(node.get("node_id", "unknown")),
                        title=node.get("label", "Unknown File"),
                        type="asset",
                        subtitle=node.get("path", "File"),
                        url=f"/assets/{node.get('node_id', '')}",
                    )
                )
            else:
                # E.g. KEY, CERTIFICATE, ALGORITHM usage
                algo = node.get("algorithm", "")
                results.append(
                    SearchResult(
                        id=str(node.get("node_id", "unknown")),
                        title=node.get("label", "Unknown Asset"),
                        type="asset",
                        subtitle=f"{label} • {algo}" if algo else label,
                        url=f"/assets/{node.get('node_id', '')}",
                    )
                )

        return results
    except Exception:
        return []
