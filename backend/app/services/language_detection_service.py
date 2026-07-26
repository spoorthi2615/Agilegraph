from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
from app.models.language import DetectedLanguage

class LanguageDetectionService:
    """
    Service responsible for recursively scanning a project directory to detect
    the programming languages used, based on source files and ecosystem manifests.
    """

    # Mapping of programming languages to their indicator rules.
    # Rules contain exact filenames (e.g., 'pom.xml') or file extensions (e.g., '.py').
    LANGUAGE_RULES = {
        "Python": {".py", "requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock"},
        "Java": {".java", "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"},
        "Go": {".go", "go.mod", "go.sum"},
        "JavaScript": {".js", "package.json", "yarn.lock"},
        "TypeScript": {".ts", "tsconfig.json", "package.json"},
        "C#": {".cs", ".csproj", ".sln"},
        "Rust": {".rs", "Cargo.toml", "Cargo.lock"},
    }

    # Directories to completely ignore during recursive traversal to prevent
    # performance issues and false positives from dependencies or build artifacts.
    IGNORED_DIRS = {
        ".git", ".github", "node_modules", "venv", ".venv", 
        "__pycache__", "dist", "build", "target", "bin", 
        "obj", "vendor", "coverage", ".idea", ".vscode"
    }

    @staticmethod
    def detect_languages(project_path: Path) -> List[DetectedLanguage]:
        """
        Recursively scans the provided project_path to detect programming languages.
        
        Args:
            project_path (Path): The root directory of the extracted project.
            
        Returns:
            List[DetectedLanguage]: A list of detected languages containing confidence scores and indicators.
        """
        if not project_path.exists() or not project_path.is_dir():
            return []

        # Dictionary to accumulate found indicators grouped by language
        found_indicators: Dict[str, Set[str]] = defaultdict(set)
        
        # Iterative BFS traversal using pathlib to allow directory pruning
        dirs_to_scan = [project_path]
        
        while dirs_to_scan:
            current_dir = dirs_to_scan.pop()
            
            try:
                for path in current_dir.iterdir():
                    if path.is_dir():
                        if path.name not in LanguageDetectionService.IGNORED_DIRS:
                            dirs_to_scan.append(path)
                    elif path.is_file():
                        filename = path.name
                        extension = path.suffix.lower()
                        
                        # Cross-reference the current file against all defined language rules
                        for language, rules in LanguageDetectionService.LANGUAGE_RULES.items():
                            if filename in rules:
                                found_indicators[language].add(filename)
                            elif extension in rules:
                                found_indicators[language].add(extension)
            except PermissionError:
                # Silently skip directories we cannot read
                continue
                    
        results: List[DetectedLanguage] = []
        
        # Evaluate findings to calculate confidence scores
        for language, indicators in found_indicators.items():
            if not indicators:
                continue
                
            confidence = 0.0
            
            # Segregate indicators into ecosystem files (e.g., pom.xml) and source extensions (e.g., .py)
            extensions_found = [ind for ind in indicators if ind.startswith('.')]
            ecosystem_files_found = [ind for ind in indicators if not ind.startswith('.')]
            
            # C# uses extensions for its project files, so we adjust categorization for logic
            if language == "C#":
                if ".csproj" in extensions_found:
                    ecosystem_files_found.append(".csproj")
                    extensions_found.remove(".csproj")
                if ".sln" in extensions_found:
                    ecosystem_files_found.append(".sln")
                    extensions_found.remove(".sln")
            
            # Heuristic Confidence Calculation:
            if ecosystem_files_found and extensions_found:
                # Strongest confidence: Both project management files and actual source code are present
                confidence = 1.0
            elif ecosystem_files_found:
                # High confidence: Ecosystem file exists, implying the project relies on this language
                confidence = 0.8
            elif extensions_found:
                # Moderate confidence: Only source files found without formal project management files
                confidence = 0.6
                
            results.append(
                DetectedLanguage(
                    language=language,
                    confidence=confidence,
                    indicators=sorted(list(indicators))
                )
            )
            
        # Return results sorted by confidence (highest first)
        return sorted(results, key=lambda x: x.confidence, reverse=True)
