from typing import List, Dict
from collections import defaultdict

from app.models.expert_validation import ExpertValidation
from app.models.statistical_validation_report import StatisticalValidationReport
from app.services.inter_rater_reliability_service import InterRaterReliabilityService
from app.services.fleiss_kappa_service import FleissKappaService

class StatisticalValidationWorkflowService:
    """
    Orchestration service responsible for aggregating raw expert validations across 
    an entire repository, routing them to the appropriate statistical math engine, 
    and compiling a unified macroscopic validation report.
    """

    @classmethod
    def generate_report(
        cls, 
        validations: List[ExpertValidation], 
        reliability_threshold: float = 0.60
    ) -> StatisticalValidationReport:
        """
        Groups all raw validations by their originating node, dynamically routes arrays of exactly 
        2 experts to Cohen's Kappa and arrays of 3+ experts to Fleiss' Kappa, and computes 
        repository-wide averages without duplicating any mathematical algorithms.
        """
        if not validations:
            raise ValueError("Cannot generate a macroscopic statistical report on an empty list of validations.")
            
        total_expert_validations = len(validations)
            
        # 1. Group validations by node_id
        grouped_validations: Dict[str, List[ExpertValidation]] = defaultdict(list)
        for v in validations:
            grouped_validations[v.node_id].append(v)
            
        pairwise_results = []
        multi_rater_results = []
        
        high_reliability_nodes = []
        low_reliability_nodes = []
        
        # 2. Orchestrate and route to specific mathematical engines
        for node_id, node_validations in grouped_validations.items():
            num_experts = len(node_validations)
            
            # Nodes with exactly 1 expert cannot be mathematically evaluated for inter-rater reliability,
            # so they are safely skipped in the statistical calculation phase.
            
            if num_experts == 2:
                # Exactly 2 experts: Safely delegate to the dedicated pairwise Cohen's Kappa service
                result = InterRaterReliabilityService.calculate_kappa(node_validations[0], node_validations[1])
                pairwise_results.append(result)
                
                # Classify node reliability using the injected threshold
                if result.cohens_kappa >= reliability_threshold:
                    high_reliability_nodes.append(node_id)
                else:
                    low_reliability_nodes.append(node_id)
                    
            elif num_experts >= 3:
                # 3 or more experts: Safely delegate to the dedicated multi-rater Fleiss' Kappa service
                result = FleissKappaService.calculate_kappa(node_validations)
                multi_rater_results.append(result)
                
                if result.fleiss_kappa >= reliability_threshold:
                    high_reliability_nodes.append(node_id)
                else:
                    low_reliability_nodes.append(node_id)
                
        # 3. Compute repository-level summary metrics
        total_nodes = len(grouped_validations)
        
        avg_cohens = 0.0
        if pairwise_results:
            avg_cohens = sum(r.cohens_kappa for r in pairwise_results) / len(pairwise_results)
            
        avg_fleiss = 0.0
        if multi_rater_results:
            avg_fleiss = sum(r.fleiss_kappa for r in multi_rater_results) / len(multi_rater_results)
            
        # 4. Generate macroscopic summary narrative
        summary = (
            f"Statistically analyzed {total_nodes} nodes across {total_expert_validations} total validations. "
            f"Generated {len(pairwise_results)} Cohen's Kappa pairwise analyses and "
            f"{len(multi_rater_results)} Fleiss' Kappa multi-rater analyses. "
            f"Identified {len(high_reliability_nodes)} high-reliability consensus nodes and "
            f"{len(low_reliability_nodes)} low-reliability highly-contested nodes."
        )
        
        # 5. Return the unified DTO payload
        return StatisticalValidationReport(
            total_nodes_validated=total_nodes,
            total_expert_validations=total_expert_validations,
            pairwise_reliability_results=pairwise_results,
            multi_rater_reliability_results=multi_rater_results,
            average_cohens_kappa=avg_cohens,
            average_fleiss_kappa=avg_fleiss,
            high_reliability_nodes=high_reliability_nodes,
            low_reliability_nodes=low_reliability_nodes,
            summary=summary,
            metadata={
                "high_reliability_threshold": reliability_threshold
            }
        )
