import logging
from typing import Any, Dict

from app.cbom.cbom_config import CBOMConfig

logger = logging.getLogger(__name__)


class CBOMValidator:
    """
    Performs pre-flight validation on raw CBOM JSON payloads.
    """

    def __init__(self, config: CBOMConfig):
        self.config = config

    def validate_raw_json(self, raw_data: Dict[str, Any]) -> bool:
        """
        Validates structure, duplicate IDs, and required fields.
        Returns True if valid, False otherwise.
        """
        if not raw_data:
            logger.error("CBOM Validation Failed: Empty payload.")
            return False

        format_type = raw_data.get("format")
        if format_type not in self.config.supported_formats:
            logger.error(f"CBOM Validation Failed: Unsupported format '{format_type}'.")
            return False

        if "document_id" not in raw_data:
            logger.error("CBOM Validation Failed: Missing 'document_id'.")
            return False

        assets = raw_data.get("crypto_assets", [])
        if not isinstance(assets, list):
            logger.error("CBOM Validation Failed: 'crypto_assets' must be a list.")
            return False

        seen_ids = set()
        for i, asset in enumerate(assets):
            if not isinstance(asset, dict):
                logger.error(f"CBOM Validation Failed: Asset at index {i} is not a dictionary.")
                return False

            if "algorithm" not in asset:
                logger.error(f"CBOM Validation Failed: Asset at index {i} missing 'algorithm'.")
                return False

            asset_id = asset.get("asset_id")
            if self.config.require_asset_identifiers and not asset_id:
                logger.error(f"CBOM Validation Failed: Asset at index {i} missing 'asset_id'.")
                return False

            if asset_id:
                if asset_id in seen_ids:
                    logger.error(f"CBOM Validation Failed: Duplicate asset_id '{asset_id}'.")
                    return False
                seen_ids.add(asset_id)

        return True
