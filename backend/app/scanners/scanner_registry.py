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


def get_default_registry() -> ScannerRegistry:
    """
    Factory function to instantiate a registry and pre-register all standard scanners.
    """
    from app.scanners.certificate_scanner import CertificateScanner
    from app.scanners.ct_scanner import CTScanner
    from app.scanners.dependency_scanner import DependencyScanner
    from app.scanners.go_scanner import GoScanner
    from app.scanners.java_scanner import JavaScanner
    from app.scanners.python_scanner import PythonScanner
    from app.scanners.semgrep_scanner import SemgrepScanner

    registry = ScannerRegistry()
    registry.register(PythonScanner)
    registry.register(DependencyScanner)
    registry.register(CertificateScanner)
    registry.register(JavaScanner)
    registry.register(GoScanner)
    registry.register(SemgrepScanner)
    registry.register(CTScanner)
    return registry
