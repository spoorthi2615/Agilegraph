from typing import List, Dict, Any
from neo4j import GraphDatabase, Transaction

class GraphQueryService:
    """
    Provides secure, read-only querying capabilities against the Neo4j database,
    acting as the data access layer for future dashboards and analytics.
    """
    def __init__(self, uri: str, user: str, password: str) -> None:
        if not uri:
            self.driver = None
            return
        
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            connection_timeout=3,           # Fail fast if Neo4j unreachable
            max_connection_lifetime=300
        )

    def close(self) -> None:
        self.driver.close()

    def get_high_risk_assets(self) -> List[Dict[str, Any]]:
        """
        Returns all nodes in the graph that possess a critical risk score (>= 75).
        """
        query = """
        MATCH (n)
        WHERE n.risk_score >= 75
        RETURN n
        """
        with self.driver.session() as session:
            return session.execute_read(self._execute_and_fetch, query)

    def get_all_assets(self) -> List[Dict[str, Any]]:
        """
        Returns all cryptographic assets in the graph.
        """
        query = """
        MATCH (n)
        WHERE NOT n:FILE AND NOT n:DEPENDENCY AND NOT n:CERTIFICATE
        RETURN n
        """
        with self.driver.session() as session:
            return session.execute_read(self._execute_and_fetch, query)

    def get_files_using_dependency(self, package_name: str) -> List[Dict[str, Any]]:
        """
        Traverses the graph to find all Python files that IMPORT a specific vulnerable dependency.
        Uses parameterized Cypher to prevent injection attacks.
        """
        query = """
        MATCH (f:FILE)-[:USES]->(d:DEPENDENCY)
        WHERE toLower(d.label) = toLower($package_name)
        RETURN f
        """
        with self.driver.session() as session:
            return session.execute_read(self._execute_and_fetch, query, {"package_name": package_name})

    def get_assets_in_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Traverses the graph to find all cryptographic assets structurally contained within a specific file.
        Uses parameterized Cypher to prevent injection attacks.
        """
        query = """
        MATCH (f:FILE)-[:CONTAINS]->(a)
        WHERE f.file_path = $file_path
        RETURN a
        """
        with self.driver.session() as session:
            return session.execute_read(self._execute_and_fetch, query, {"file_path": file_path})

    def get_summary_statistics(self) -> Dict[str, int]:
        """
        Calculates aggregate macro-statistics of the entire graph by running
        a series of highly optimized count queries within a single read transaction.
        """
        def _get_stats(tx: Transaction) -> Dict[str, int]:
            # Neo4j optimizes simple count() queries using the internal count store.
            total_nodes = tx.run("MATCH (n) RETURN count(n) as count").single()["count"]
            total_relationships = tx.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            file_count = tx.run("MATCH (n:FILE) RETURN count(n) as count").single()["count"]
            dependency_count = tx.run("MATCH (n:DEPENDENCY) RETURN count(n) as count").single()["count"]
            certificate_count = tx.run("MATCH (n:CERTIFICATE) RETURN count(n) as count").single()["count"]
            
            # Asset count is calculated as anything that isn't a File, Dependency, or Certificate
            asset_count_query = """
            MATCH (n) 
            WHERE NOT n:FILE AND NOT n:DEPENDENCY AND NOT n:CERTIFICATE 
            RETURN count(n) as count
            """
            asset_count = tx.run(asset_count_query).single()["count"]
            
            return {
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
                "file_count": file_count,
                "asset_count": asset_count,
                "dependency_count": dependency_count,
                "certificate_count": certificate_count
            }
            
        with self.driver.session() as session:
            return session.execute_read(_get_stats)

    def get_dashboard_aggregations(self) -> Dict[str, Any]:
        """
        Executes aggregation queries for the dashboard to populate risk distribution,
        algorithm usage, and critical alerts from Neo4j.
        """
        def _get_aggs(tx: Transaction) -> Dict[str, Any]:
            # Severity counts
            severity_query = """
            MATCH (n) 
            WHERE NOT n:FILE AND NOT n:DEPENDENCY AND NOT n:CERTIFICATE 
              AND n.severity IS NOT NULL
            RETURN n.severity AS severity, count(n) AS count
            """
            severities = tx.run(severity_query).data()
            
            # Algorithm counts
            algo_query = """
            MATCH (n)
            WHERE NOT n:FILE AND NOT n:DEPENDENCY AND NOT n:CERTIFICATE 
              AND n.algorithm IS NOT NULL
            RETURN n.algorithm AS algorithm, count(n) AS count
            ORDER BY count DESC
            LIMIT 7
            """
            algorithms = tx.run(algo_query).data()
            
            # Top critical alerts
            alerts_query = """
            MATCH (n)
            WHERE NOT n:FILE AND NOT n:DEPENDENCY AND NOT n:CERTIFICATE 
              AND toUpper(n.severity) = 'CRITICAL'
            RETURN n.node_id AS id, n.label AS title, 'Critical cryptographic risk detected' AS reason, n.risk_score AS score
            ORDER BY n.risk_score DESC
            LIMIT 5
            """
            alerts = tx.run(alerts_query).data()
            
            return {
                "severities": severities,
                "algorithms": algorithms,
                "alerts": alerts
            }
            
        with self.driver.session() as session:
            return session.execute_read(_get_aggs)

    def get_entire_graph(self) -> Dict[str, Any]:
        """
        Retrieves all nodes and edges from the graph.
        """
        def _get_graph(tx: Transaction) -> Dict[str, Any]:
            nodes_query = "MATCH (n) RETURN n"
            edges_query = "MATCH (n)-[r]->(m) RETURN n.node_id AS source, m.node_id AS target, type(r) AS type"
            
            nodes_result = tx.run(nodes_query)
            edges_result = tx.run(edges_query)
            
            nodes = [dict(record["n"]) for record in nodes_result]
            edges = [dict(record) for record in edges_result]
            
            return {"nodes": nodes, "edges": edges}
            
        with self.driver.session() as session:
            return session.execute_read(_get_graph)

    def get_node_by_id(self, node_id: str) -> Dict[str, Any]:
        """
        Retrieves a single node by its node_id.
        """
        query = "MATCH (n {node_id: $node_id}) RETURN n"
        with self.driver.session() as session:
            result = session.execute_read(self._execute_and_fetch, query, {"node_id": node_id})
            if result:
                return result[0]
            return {}

    @staticmethod
    def _execute_and_fetch(tx: Transaction, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Internal helper to execute a query and safely map the resulting Neo4j Node objects
        back into standard Python dictionaries.
        """
        if parameters is None:
            parameters = {}
        result = tx.run(query, parameters)
        
        # We assume queries are structured to RETURN exactly one alias (e.g., RETURN n, RETURN f)
        # We extract the first value of the record, which is the Neo4j Node object, and dict() it.
        return [dict(record.values()[0]) for record in result]
