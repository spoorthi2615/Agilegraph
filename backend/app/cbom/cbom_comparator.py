import logging
from typing import List

from app.cbom.cbom_model import CBOMAsset, CBOMComparison, CBOMInventory

logger = logging.getLogger(__name__)


class CBOMComparator:
    """
    Implements a bidirectional diff between a theoretical CBOM baseline and AgileGraph's empirical discovery.
    """

    def compare(
        self, cbom_inventory: CBOMInventory, discovered_assets: List[CBOMAsset]
    ) -> CBOMComparison:
        """
        Executes the comparison logic immutably.
        """
        result = CBOMComparison()

        cbom_map = {asset.asset_id: asset for asset in cbom_inventory.assets}
        disc_map = {asset.asset_id: asset for asset in discovered_assets}

        for asset_id, c_asset in cbom_map.items():
            if asset_id in disc_map:
                d_asset = disc_map[asset_id]

                # Check for mismatches in critical fields
                mismatches = {}
                if c_asset.algorithm != d_asset.algorithm:
                    mismatches["algorithm"] = {
                        "cbom": c_asset.algorithm,
                        "discovered": d_asset.algorithm,
                    }
                if c_asset.version and d_asset.version and c_asset.version != d_asset.version:
                    mismatches["version"] = {"cbom": c_asset.version, "discovered": d_asset.version}
                if c_asset.key_size and d_asset.key_size and c_asset.key_size != d_asset.key_size:
                    mismatches["key_size"] = {
                        "cbom": c_asset.key_size,
                        "discovered": d_asset.key_size,
                    }

                if mismatches:
                    result.mismatched_assets.append(
                        {"asset_id": asset_id, "mismatches": mismatches}
                    )
                else:
                    result.matched_assets.append(c_asset.model_copy())
            else:
                # In CBOM but not in AgileGraph discovery
                result.unexpected_assets.append(c_asset.model_copy())

        for asset_id, d_asset in disc_map.items():
            if asset_id not in cbom_map:
                # Discovered by AgileGraph but missing from theoretical CBOM
                result.missing_assets.append(d_asset.model_copy())

        result.summary = {
            "total_cbom_assets": len(cbom_inventory.assets),
            "total_discovered_assets": len(discovered_assets),
            "matched_assets": len(result.matched_assets),
            "missing_from_cbom": len(result.missing_assets),
            "unexpected_in_cbom": len(result.unexpected_assets),
            "mismatched_assets": len(result.mismatched_assets),
        }

        return result
