import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class WorkflowLogger:
    """
    High-precision timing utility for profiling mathematical phase execution duration.
    """
    def __init__(self):
        self.timers: Dict[str, float] = {}
        self.durations: Dict[str, float] = {}
        
    def start(self, phase: str):
        self.timers[phase] = time.perf_counter()
        logger.info(f"--- Starting Phase: {phase} ---")
        
    def end(self, phase: str):
        if phase in self.timers:
            duration = time.perf_counter() - self.timers[phase]
            self.durations[phase] = duration
            logger.info(f"--- Completed Phase: {phase} in {duration:.4f}s ---")
        else:
            logger.warning(f"Phase {phase} was not started.")
            
    def get_durations(self) -> Dict[str, float]:
        return self.durations
