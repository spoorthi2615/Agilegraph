import logging
import json
from typing import List, Dict, Any, Optional
from app.cbom.cbom_parser import CBOMParser
from app.cbom.cbom_comparator import CBOMComparator
from app.cbom.cbom_model import CBOMAsset, CBOMComparison

logger = logging.getLogger(__name__)

class CBOMService:
    """
    Facade orchestrator for CBOM Integration.
    Strictly follows Dependency Inversion.
    """
    def __init__(self, parser: CBOMParser, comparator: CBOMComparator):
        self.parser = parser
        self.comparator = comparator
        
    def process_and_compare(self, raw_json_str: str, discovered_assets: List[CBOMAsset]) -> Optional[CBOMComparison]:
        """
        Parses the raw JSON string into a CBOMInventory and compares it against AgileGraph findings.
        Returns the CBOMComparison object.
        """
        try:
            raw_data = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            logger.error(f"CBOM Service failed to decode JSON: {e}")
            return None
            
        inventory = self.parser.parse(raw_data)
        if not inventory:
            logger.error("CBOM parsing/validation failed.")
            return None
            
        logger.info(f"Successfully parsed CBOM '{inventory.document_id}' with {len(inventory.assets)} assets.")
        
        comparison = self.comparator.compare(inventory, discovered_assets)
        
        logger.info(f"Comparison complete: {comparison.summary['matched_assets']} matched, "
                    f"{comparison.summary['missing_from_cbom']} missing from CBOM, "
                    f"{comparison.summary['unexpected_in_cbom']} unexpected in CBOM.")
                    
        return comparison
