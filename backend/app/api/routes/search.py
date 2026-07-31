from fastapi import APIRouter, Depends, Query
from typing import List
from app.models.topbar import SearchResult
from app.services.graph_query_service import GraphQueryService
from app.config.settings import settings

def get_query_service():
    service = GraphQueryService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USERNAME,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        service.close()

router = APIRouter()

@router.get("/all", response_model=List[SearchResult])
def search_graph(
    q: str = Query("", description="Search query"),
    query_service: GraphQueryService = Depends(get_query_service)
) -> List[SearchResult]:
    if not q or len(q) < 2:
        return []

    # Simple Cypher query to find nodes matching the query in name, algorithm, or type
    cypher = """
    MATCH (n)
    WHERE toLower(n.name) CONTAINS toLower($q) 
       OR toLower(n.algorithm) CONTAINS toLower($q)
       OR toLower(labels(n)[0]) CONTAINS toLower($q)
    RETURN n, labels(n)[0] AS label
    LIMIT 10
    """
    
    with query_service.driver.session() as session:
        result = session.run(cypher, q=q)
        results = []
        for record in result:
            node = record["n"]
            label = record["label"]
            
            # Map node to SearchResult based on label
            if label == "PROJECT":
                results.append(SearchResult(
                    id=node.get("id", "unknown"),
                    title=node.get("name", "Unknown Project"),
                    type="scan",
                    subtitle="Project Repository",
                    url=f"/scan"
                ))
            elif label == "FILE":
                results.append(SearchResult(
                    id=node.get("id", "unknown"),
                    title=node.get("name", "Unknown File"),
                    type="asset",
                    subtitle=node.get("path", "File"),
                    url=f"/assets/{node.get('id', '')}"
                ))
            else:
                # E.g. KEY, CERTIFICATE, ALGORITHM usage
                algo = node.get("algorithm", "")
                results.append(SearchResult(
                    id=node.get("id", "unknown"),
                    title=node.get("name", "Unknown Asset"),
                    type="asset",
                    subtitle=f"{label} • {algo}" if algo else label,
                    url=f"/assets/{node.get('id', '')}"
                ))
                
        return results
