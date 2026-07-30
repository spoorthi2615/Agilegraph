import numpy as np
from typing import List, Tuple

class AHPLiteService:
    """
    Implements the Analytic Hierarchy Process (AHP) lite version for pairwise comparison
    of criteria to derive objective weights, as described in the AgileGraph methodology.
    """
    
    # Standard Random Index (RI) values for n up to 10
    RANDOM_INDEX = {
        1: 0.0,
        2: 0.0,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49
    }

    @staticmethod
    def calculate_weights(matrix: List[List[float]]) -> Tuple[List[float], float, bool]:
        """
        Calculates the priority weights and consistency ratio for a given pairwise comparison matrix.
        
        Args:
            matrix: A square, reciprocal matrix of pairwise comparisons.
            
        Returns:
            Tuple containing:
            - List of priority weights (normalized principal eigenvector)
            - Consistency Ratio (CR)
            - Boolean indicating if the matrix is consistent (CR < 0.1)
        """
        mat = np.array(matrix)
        n = mat.shape[0]
        
        # Input validation
        if n != mat.shape[1]:
            raise ValueError("The comparison matrix must be square.")
        if n < 1:
            raise ValueError("Matrix cannot be empty.")
            
        # For n=1 or n=2, consistency is always perfect (CR = 0)
        if n == 1:
            return [1.0], 0.0, True
        if n == 2:
            weights = mat[:, 0] / np.sum(mat[:, 0])  # Simple normalization for 2x2
            return weights.tolist(), 0.0, True

        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(mat)
        
        # Find the maximum eigenvalue (principal eigenvalue)
        max_index = np.argmax(np.real(eigenvalues))
        lambda_max = np.real(eigenvalues[max_index])
        
        # Extract the principal eigenvector
        principal_eigenvector = np.real(eigenvectors[:, max_index])
        
        # Normalize the principal eigenvector to sum to 1
        weights = principal_eigenvector / np.sum(principal_eigenvector)
        
        # Calculate Consistency Index (CI)
        ci = (lambda_max - n) / (n - 1)
        
        # Get Random Index (RI)
        ri = AHPLiteService.RANDOM_INDEX.get(n, 1.49) # Fallback to 1.49 for n>10, though rare in AHP
        
        # Calculate Consistency Ratio (CR)
        if ri == 0:
            cr = 0.0
        else:
            cr = ci / ri
            
        is_consistent = bool(cr < 0.10)
        
        return weights.tolist(), float(cr), is_consistent
