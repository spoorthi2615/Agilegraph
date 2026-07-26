from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from app.scanners.scanner_result import ScannerResult

class BaseScanner(ABC):
    """
    Abstract base class defining the contract for all project scanners.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The unique name of the scanner.
        """
        pass
        
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """
        A list of programming languages this scanner supports.
        """
        pass
        
    @abstractmethod
    def scan(self, project_path: Path) -> ScannerResult:
        """
        Executes the scan against the given project directory.
        """
        pass
