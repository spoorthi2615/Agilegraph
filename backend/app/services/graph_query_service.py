from typing import List, Dict, Any
from neo4j import GraphDatabase, Transaction

class GraphQueryService:
    """
    Provides secure, read-only querying capabilities against the Neo4j database,
    acting as the data access layer for future dashboards and analytics.
    """
    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

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
