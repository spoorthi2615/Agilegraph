import networkx as nx
import hashlib
import requests
import json
import os
import sys

# Ensure backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.schema.graph_schema import NodeType, EdgeType
from backend.core.risk_calculator import RiskCalculator

class GraphBuilder:
    """
    Constructs the Heterogeneous Graph from disconnected scanner outputs.
    
    Warning regarding Phase 5 GNN Training:
    This builder injects `base_risk` directly into the properties of `CRYPTO_USAGE` and `CERTIFICATE` nodes. 
    If the eventual GNN training labels are derived from this exact same Mosca-ratio formula, the model 
    may trivially learn to echo this `base_risk` feature back out instead of learning true structural 
    propagation from the graph topology. Be sure to mask or drop this feature during training if using it as a label.
    """
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.risk_calc = RiskCalculator()

    def _generate_id(self, *parts) -> str:
        """Deterministic short hash for node IDs."""
        raw = ":".join(str(p) for p in parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def ingest_code_scan(self, findings: list):
        for f in findings:
            filepath = f.get("file", "unknown")
            line = f.get("line", 0)
            algo_hint = f.get("algorithm_hint", "")
            algorithm = f.get("algorithm", "UNKNOWN")
            snippet = f.get("snippet", "")
            
            # Guard against unauthenticated Semgrep placeholder
            if snippet == "requires login":
                snippet = None
                
            # 1. Create CODE_FILE node
            file_id = f"file:{filepath}"
            if not self.graph.has_node(file_id):
                self.graph.add_node(file_id, type=NodeType.CODE_FILE.value, properties={"filepath": filepath})
                
            # 2. Create CRYPTO_USAGE node
            usage_id = "crypto:" + self._generate_id(filepath, line, algo_hint)
            
            # Compute base risk directly
            try:
                # Defaulting to 1 year shelf life and 0.5 year migration as standard code instantiation baseline
                base_risk = self.risk_calc.calculate_base_risk(algorithm, data_shelf_life_years=1, migration_time_years=0.5)
            except ValueError:
                base_risk = 1.0
                
            if not self.graph.has_node(usage_id):
                self.graph.add_node(
                    usage_id, 
                    type=NodeType.CRYPTO_USAGE.value, 
                    properties={
                        "algorithm": algorithm,
                        "algorithm_hint": algo_hint,
                        "line": line,
                        "snippet": snippet,
                        "base_risk": base_risk
                    }
                )
                
            # 3. Connect them
            # We use a static key 'usage_link' because there is only one logical edge between a specific file and a specific usage.
            # In MultiDiGraph, add_edge with an existing key will UPDATE the existing edge rather than duplicating it.
            self.graph.add_edge(file_id, usage_id, key="usage_link", type=EdgeType.USES_CRYPTO.value, properties={})

    def ingest_cert_scan(self, findings: list):
        for f in findings:
            if f.get("status") != "success":
                continue
                
            endpoint = f.get("endpoint", "unknown")
            algorithm = f.get("algorithm", "UNKNOWN")
            key_size = f.get("key_size", 0)
            expiry_str = f.get("expiry_date", "")
            
            # 1. Create NETWORK_ENDPOINT node
            ep_id = f"endpoint:{endpoint}"
            if not self.graph.has_node(ep_id):
                self.graph.add_node(ep_id, type=NodeType.NETWORK_ENDPOINT.value, properties={"endpoint": endpoint})
                
            # 2. Create CERTIFICATE node
            cert_id = "cert:" + self._generate_id(endpoint, expiry_str, algorithm, key_size)
            
            try:
                base_risk = self.risk_calc.evaluate_certificate_risk(expiry_str, algorithm)
            except Exception:
                base_risk = 1.0
                
            if not self.graph.has_node(cert_id):
                self.graph.add_node(
                    cert_id, 
                    type=NodeType.CERTIFICATE.value, 
                    properties={
                        "algorithm": algorithm,
                        "key_size": key_size,
                        "expiry_date": expiry_str,
                        "base_risk": base_risk
                    }
                )
                
            # 3. Connect them
            self.graph.add_edge(cert_id, ep_id, key="secures_link", type=EdgeType.SECURES_ENDPOINT.value, properties={})
            self.graph.add_edge(ep_id, cert_id, key="hosts_link", type=EdgeType.HOSTS_CERTIFICATE.value, properties={})

    def ingest_dependency_scan(self, findings: list):
        for f in findings:
            filepath = f.get("file", "unknown")
            library = f.get("library", "unknown")
            ecosystem = f.get("ecosystem", "unknown")
            version = f.get("version", "unknown")
            
            # 1. Create CODE_FILE node for the manifest
            file_id = f"file:{filepath}"
            if not self.graph.has_node(file_id):
                self.graph.add_node(file_id, type=NodeType.CODE_FILE.value, properties={"filepath": filepath})
                
            # 2. Create LIBRARY node
            lib_id = "lib:" + self._generate_id(ecosystem, library, version)
            
            if not self.graph.has_node(lib_id):
                self.graph.add_node(
                    lib_id, 
                    type=NodeType.LIBRARY.value, 
                    properties={
                        "library": library,
                        "ecosystem": ecosystem,
                        "version": version
                    }
                )
                
            # 3. Check OSV Vulnerability
            osv_results = self._check_osv_vulnerability(library, version, ecosystem)
            
            # 4. Connect them
            edge_props = {}
            edge_type = EdgeType.HAS_VULNERABILITY.value if (osv_results is not None and len(osv_results) > 0) else EdgeType.DEPENDS_ON.value
            
            if osv_results is None:
                # API failure / network error - we don't know if it's vulnerable
                edge_props["osv_query_failed"] = True
                edge_props["needs_manual_review"] = True
            elif osv_results: # list with actual CVEs
                edge_props["osv_hits"] = len(osv_results)
                if version == "unknown":
                    edge_props["needs_manual_review"] = True
                    
            # Using a static 'dependency_link' key ensures that if a library's status changes from DEPENDS_ON to 
            # HAS_VULNERABILITY on a re-scan, the edge is updated/overwritten in place rather than duplicated.
            self.graph.add_edge(file_id, lib_id, key="dependency_link", type=edge_type, properties=edge_props)

    def _check_osv_vulnerability(self, library: str, version: str, ecosystem: str) -> list:
        """
        Queries api.osv.dev for known vulnerabilities.
        If version is 'unknown', it queries the base package and returns all known vulns,
        which will be flagged for manual review in the graph.
        """
        # Ecosystem mapping for OSV
        eco_map = {
            "python": "PyPI",
            "java": "Maven",
            "go": "Go"
        }
        osv_eco = eco_map.get(ecosystem.lower(), ecosystem)
        
        payload = {
            "package": {
                "name": library,
                "ecosystem": osv_eco
            }
        }
        
        if version != "unknown":
            payload["version"] = version
            
        try:
            resp = requests.post("https://api.osv.dev/v1/query", json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("vulns", [])
            else:
                print(f"OSV query returned HTTP {resp.status_code} for {library}")
                return None
        except Exception as e:
            print(f"OSV query failed for {library}: {e}")
            
        return None

if __name__ == "__main__":
    # Test block loading from real JSON files if they exist
    import sys
    
    builder = GraphBuilder()
    
    # Try to load real data
    code_file = "test_data/code_findings.json"
    cert_file = "test_data/cert_findings.json"
    dep_file = "test_data/dep_findings.json"
    
    if os.path.exists(code_file):
        with open(code_file, 'r') as f:
            builder.ingest_code_scan(json.load(f))
            print(f"Ingested {code_file}")
            
    if os.path.exists(cert_file):
        with open(cert_file, 'r') as f:
            # Cert scanner returns a single dict, but ingest takes a list
            data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            builder.ingest_cert_scan(data)
            print(f"Ingested {cert_file}")
            
    if os.path.exists(dep_file):
        with open(dep_file, 'r') as f:
            builder.ingest_dependency_scan(json.load(f))
            print(f"Ingested {dep_file}")
            
    print(f"Built graph with {builder.graph.number_of_nodes()} nodes and {builder.graph.number_of_edges()} edges.")
    
    # Print node types breakdown
    from collections import Counter
    node_types = Counter(nx.get_node_attributes(builder.graph, 'type').values())
    for nt, count in node_types.items():
        print(f" - {nt}: {count}")
