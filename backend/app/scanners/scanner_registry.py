from typing import Dict, List, Type
from app.scanners.base_scanner import BaseScanner

class ScannerRegistry:
    """
    Central registry for managing available scanners in the system.
    """
    def __init__(self) -> None:
        self._scanners: Dict[str, Type[BaseScanner]] = {}
        
    def register(self, scanner_class: Type[BaseScanner]) -> None:
        """
        Registers a scanner class into the registry.
        """
        # Instantiate temporarily to read the name property
        name = scanner_class().name
        if name in self._scanners:
            raise ValueError(f"Scanner with name '{name}' is already registered.")
        self._scanners[name] = scanner_class
        
    def get(self, scanner_name: str) -> Type[BaseScanner]:
        """
        Retrieves a scanner class by its name.
        """
        if scanner_name not in self._scanners:
            raise KeyError(f"Scanner '{scanner_name}' not found in registry.")
        return self._scanners[scanner_name]
        
    def list_scanners(self) -> List[str]:
        """
        Returns a list of all registered scanner names.
        """
        return list(self._scanners.keys())
