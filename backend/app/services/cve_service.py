import json
import os
from typing import List, Dict, Any

class CVEService:
    """
    Service for looking up vulnerabilities in dependencies.
    Utilizes a bundled snapshot of NVD data to maintain offline capability.
    """
    _snapshot_cache: Dict[str, List[Dict[str, Any]]] = None

    @classmethod
    def _load_snapshot(cls) -> Dict[str, List[Dict[str, Any]]]:
        if cls._snapshot_cache is None:
            snapshot_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "data", 
                "nvd_snapshot.json"
            )
            try:
                with open(snapshot_path, "r", encoding="utf-8") as f:
                    cls._snapshot_cache = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                cls._snapshot_cache = {}
        return cls._snapshot_cache

    @classmethod
    def lookup_cves(
        cls, dependency_name: str, version: str = None
    ) -> List[Dict[str, Any]]:
        """
        Looks up CVEs for a given dependency name.
        Note: Exact version matching ranges are simplified for this implementation.
        Matches base dependency names against the NVD snapshot.
        """
        snapshot = cls._load_snapshot()
        
        normalized_name = dependency_name.lower()
        
        # Simple substring matching for common library identifiers
        for key in snapshot.keys():
            if key in normalized_name:
                return snapshot[key]
                
        return []
