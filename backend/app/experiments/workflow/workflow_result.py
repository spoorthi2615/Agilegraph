from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class WorkflowResult(BaseModel):
    """
    Unified container holding the results from all executed pipeline phases.
    Uses 'Any' / 'dict' wrappers for phase results to cleanly orchestrate external 
    modules without circular dependency imports.
    """
    execution_times: Dict[str, float] = Field(default_factory=dict)
    
    benchmark_results: Optional[Any] = None
    ablation_results: Optional[Any] = None
    bootstrap_results: Optional[Any] = None
    significance_results: Optional[Any] = None
    
    cohens_kappa_results: Optional[Any] = None
    fleiss_kappa_results: Optional[Any] = None
    
    errors: Dict[str, str] = Field(default_factory=dict)
