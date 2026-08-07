from typing import List

from app.scanners.semgrep.semgrep_finding import SemgrepFinding


class FindingNormalizer:
    """
    Merges Semgrep findings with existing custom scanner findings immutably,
    maintaining strict deduplication keys and returning strongly typed models.
    """

    def normalize(
        self, custom_findings: List[SemgrepFinding], semgrep_findings: List[SemgrepFinding]
    ) -> List[SemgrepFinding]:
        """
        Takes strongly typed existing findings and strongly typed Semgrep findings.
        Returns a new unified list of finding objects, preserving immutability.
        """
        # Deduplication key is now (file_path, line, rule_id)
        # This prevents catastrophic false negatives when multiple distinct
        # vulnerabilities exist on the exact same line of code.

        merged_results = []

        # Copy custom findings to merged_results to preserve immutability of the input
        # We use model_copy() to create a deep copy
        for cf in custom_findings:
            merged_results.append(cf.model_copy())

        # Re-index the merged results so we can update them in place in the output list safely
        output_index = {(f.file_path, f.line, f.rule_id): f for f in merged_results}

        for sf in semgrep_findings:
            # We map the semgrep rule_id to the custom rule_id logic.
            key = (sf.file_path, sf.line, sf.rule_id)

            if key in output_index:
                # We have a true overlap. Update the source attribution on the NEW list's object.
                existing_match = output_index[key]
                existing_match.source = "Both"
                existing_match.semgrep_rule_id = sf.rule_id
            else:
                # Unique finding. Add it directly.
                merged_results.append(sf.model_copy())

        return merged_results
