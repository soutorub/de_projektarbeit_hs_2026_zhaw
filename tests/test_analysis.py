"""Statistische Methoden mit nachvollziehbaren kleinen Beispielen prüfen."""

import numpy as np
import pytest

from de_projekt.analysis import holm_adjust, independence_test


def test_independent_table_has_no_effect():
    result = independence_test([[20, 30], [40, 60]])
    assert result["chi2"] == pytest.approx(0)
    assert result["p_value"] == pytest.approx(1)
    assert result["cramers_v"] == pytest.approx(0)


def test_holm_preserves_order_and_enforces_monotonicity():
    np.testing.assert_allclose(holm_adjust([0.04, 0.01, 0.03]), [0.06, 0.03, 0.06])
    np.testing.assert_allclose(holm_adjust([0.8, 0.9]), [1, 1])


def test_sparse_table_uses_reproducible_simulation():
    first = independence_test([[1, 8], [7, 2]], seed=42, resamples=999)
    second = independence_test([[1, 8], [7, 2]], seed=42, resamples=999)
    assert first == second
    assert "Monte Carlo" in first["method"]
    assert first["expected_cells_lt5"] > 0


@pytest.mark.parametrize("table", [[[1, -1], [2, 3]], [[1.5, 2], [3, 4]], [[0, 0], [0, 0]]])
def test_invalid_tables_fail(table):
    with pytest.raises(ValueError):
        independence_test(table)
