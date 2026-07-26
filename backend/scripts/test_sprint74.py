import os
import sys
import logging
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cbom.cbom_config import CBOMConfig
from app.cbom.cbom_model import CBOMAsset
from app.cbom.cbom_validator import CBOMValidator
from app.cbom.cbom_parser import CBOMParser
from app.cbom.cbom_comparator import CBOMComparator
from app.cbom.cbom_service import CBOMService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test_sprint74():
    logging.info("Testing Sprint 73 CBOM Integration...")
    
    config = CBOMConfig()
    validator = CBOMValidator(config)
    parser = CBOMParser(validator)
    comparator = CBOMComparator()
    service = CBOMService(parser, comparator)
    
    # 1. Validation Logic
    bad_json = '{"crypto_assets": "not a list"}'
    assert service.process_and_compare(bad_json, []) is None
    
    duplicate_json = json.dumps({
        "format": "agilegraph-cbom-v1",
        "document_id": "doc123",
        "crypto_assets": [
            {"asset_id": "1", "algorithm": "AES"},
            {"asset_id": "1", "algorithm": "RSA"}
        ]
    })
    assert service.process_and_compare(duplicate_json, []) is None
    logging.info("CBOM Validator successfully rejected malformed and duplicate schemas.")
    
    # 2. Diff Comparator Engine
    cbom_json = json.dumps({
        "format": "agilegraph-cbom-v1",
        "document_id": "doc_final",
        "crypto_assets": [
            {"asset_id": "A1", "algorithm": "AES", "version": "1.0", "key_size": 256}, # Matches perfectly
            {"asset_id": "A2", "algorithm": "RSA", "version": "2.0"}, # Mismatch on version
            {"asset_id": "A3", "algorithm": "MD5"} # Unexpected (Not found by AgileGraph)
        ]
    })
    
    discovered = [
        CBOMAsset(asset_id="A1", algorithm="AES", version="1.0", key_size=256),
        CBOMAsset(asset_id="A2", algorithm="RSA", version="2.1"), # Differs in version!
        CBOMAsset(asset_id="A4", algorithm="SHA256") # Missing from CBOM!
    ]
    
    comparison = service.process_and_compare(cbom_json, discovered)
    
    assert comparison is not None
    assert len(comparison.matched_assets) == 1
    assert comparison.matched_assets[0].asset_id == "A1"
    
    assert len(comparison.mismatched_assets) == 1
    assert comparison.mismatched_assets[0]["asset_id"] == "A2"
    assert comparison.mismatched_assets[0]["mismatches"]["version"] == {"cbom": "2.0", "discovered": "2.1"}
    
    assert len(comparison.unexpected_assets) == 1
    assert comparison.unexpected_assets[0].asset_id == "A3"
    
    assert len(comparison.missing_assets) == 1
    assert comparison.missing_assets[0].asset_id == "A4"
    
    logging.info("CBOM Comparator bidirectionally mapped state perfectly.")
    
    # 3. Graph Edge Integration
    edges = comparison.to_graph_edges("doc_final")
    assert ("CBOM:doc_final", "VERIFIES", "CryptoAsset:A1") in edges
    assert ("CBOM:doc_final", "CLAIMS_PRESENCE_OF", "CryptoAsset:A3") in edges
    
    logging.info("Graph Translation mappings verified.")
    logging.info("All Sprint 73 CBOM Integration tests passed successfully!")

if __name__ == "__main__":
    test_sprint74()
