from pathlib import Path
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class DependencyMappingService:
    """
    Service responsible for inspecting project source files across various languages
    to extract import statements and generate normalized relationship telemetry.
    Strictly isolated from graph construction and GraphNode/GraphEdge creation.
    """
    
    @staticmethod
    def map_dependencies(project_path: Path) -> Dict[str, List[str]]:
        """
        Parses source files in the project to extract top-level import dependencies.
        Returns a mapping of normalized file paths to lists of imported package names (lowercased).
        """
        dependency_map: Dict[str, List[str]] = {}
        
        if not project_path.exists() or not project_path.is_dir():
            return dependency_map
            
        # Extensible point for adding Java and Go parsers in the future
        for file_path in sorted(project_path.rglob("*.py")):
            imports = DependencyMappingService._parse_python_imports(file_path)
            if imports:
                dependency_map[file_path.as_posix()] = list(imports)
                
        return dependency_map
        
    @staticmethod
    def _parse_python_imports(file_path: Path) -> Set[str]:
        """
        Heuristically extracts imported top-level modules from a Python file.
        """
        imported_packages = set()
        try:
            content = file_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("import "):
                    parts = line[7:].split(",")
                    for p in parts:
                        top_level = p.strip().split(".")[0]
                        if top_level:
                            imported_packages.add(top_level.lower())
                elif line.startswith("from "):
                    parts = line[5:].split(" import ")
                    if len(parts) >= 1:
                        top_level = parts[0].strip().split(".")[0]
                        if top_level:
                            imported_packages.add(top_level.lower())
        except Exception as e:
            logger.error(f"Error extracting imports from {file_path}: {e}")
            
        return imported_packages
