from enum import Enum
from typing import Dict


class ScanStage(str, Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    CLONING = "cloning"
    SCANNING = "scanning"
    BUILDING_GRAPH = "building_graph"
    SCORING = "scoring"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanStatusService:
    _statuses: Dict[str, str] = {}

    @classmethod
    def set_status(cls, project_id: str, status: ScanStage):
        cls._statuses[project_id] = status.value

    @classmethod
    def get_status(cls, project_id: str) -> str:
        return cls._statuses.get(project_id, "unknown")

    @classmethod
    def clear_status(cls, project_id: str):
        cls._statuses.pop(project_id, None)
