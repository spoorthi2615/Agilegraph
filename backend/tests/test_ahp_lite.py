import numpy as np
import pytest

from app.services.ahp_lite_service import AHPLiteService


def test_ahp_lite_perfect_consistency():
    # A perfectly consistent 3x3 matrix
    # Weights should be exactly [1/3, 1/3, 1/3] for all 1s
    matrix = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

    weights, cr, is_consistent = AHPLiteService.calculate_weights(matrix)

    assert np.allclose(weights, [1 / 3, 1 / 3, 1 / 3])
    assert np.isclose(cr, 0.0)
    assert is_consistent is True


def test_ahp_lite_typical_scenario():
    # A typical slightly inconsistent, but acceptable 3x3 matrix
    # Crit 1 is 3x more important than Crit 2, and 5x more important than Crit 3
    # Crit 2 is 2x more important than Crit 3
    # M = [[1, 3, 5],
    #      [1/3, 1, 2],
    #      [1/5, 1/2, 1]]
    matrix = [[1.0, 3.0, 5.0], [1 / 3, 1.0, 2.0], [1 / 5, 1 / 2, 1.0]]

    weights, cr, is_consistent = AHPLiteService.calculate_weights(matrix)

    # Expected approximate weights for this classic AHP example
    # w1 ~ 0.637, w2 ~ 0.258, w3 ~ 0.105
    assert np.isclose(weights[0], 0.648, atol=0.02)
    assert np.isclose(weights[1], 0.230, atol=0.02)
    assert np.isclose(weights[2], 0.122, atol=0.02)

    # CR should be very low (close to 0.03) and < 0.1
    assert cr < 0.1
    assert is_consistent is True


def test_ahp_lite_inconsistent_scenario():
    # An intentionally highly inconsistent matrix
    # A > B by 9, B > C by 9, but C > A by 9 (Circular logic!)
    matrix = [[1.0, 9.0, 1 / 9], [1 / 9, 1.0, 9.0], [9.0, 1 / 9, 1.0]]

    weights, cr, is_consistent = AHPLiteService.calculate_weights(matrix)

    # CR should be huge, definitely > 0.1
    assert cr > 0.1
    assert is_consistent is False


def test_ahp_lite_invalid_matrix():
    # Non-square matrix should raise ValueError
    matrix = [[1.0, 2.0], [1.0, 2.0], [1.0, 2.0]]

    with pytest.raises(ValueError):
        AHPLiteService.calculate_weights(matrix)
