import logging
from typing import Dict, Any, Optional
from app.cbom.cbom_model import CBOMAsset, CBOMInventory
from app.cbom.cbom_validator import CBOMValidator

logger = logging.getLogger(__name__)

class CBOMParser:
    """
    Parses validated JSON into strongly typed CBOMInventory models immutably.
    """
    def __init__(self, validator: CBOMValidator):
        self.validator = validator
        
    def parse(self, raw_data: Dict[str, Any]) -> Optional[CBOMInventory]:
        """
        Validates and parses the document. Returns None if validation fails.
        """
        if not self.validator.validate_raw_json(raw_data):
            return None
            
        document_id = raw_data.get("document_id", "unknown_doc")
        raw_assets = raw_data.get("crypto_assets", [])
        
        parsed_assets = []
        for ra in raw_assets:
            asset = CBOMAsset(
                asset_id=ra.get("asset_id", ""),
                algorithm=ra.get("algorithm", ""),
                library=ra.get("library"),
                version=ra.get("version"),
                key_size=ra.get("key_size"),
                certificate=ra.get("certificate"),
                provider=ra.get("provider"),
                application=ra.get("application"),
                dependency=ra.get("dependency")
            )
            parsed_assets.append(asset)
            
        return CBOMInventory(
            document_id=document_id,
            assets=parsed_assets
        )
