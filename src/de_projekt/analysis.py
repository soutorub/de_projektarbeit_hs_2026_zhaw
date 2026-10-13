"""Statistische Hilfsfunktionen für Teil 1; Auswertung im Analyse-Notebook.

Testimplementierung und Resampling-API:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
Holm: Holm (1979), A Simple Sequentially Rejective Multiple Test Procedure,
Scandinavian Journal of Statistics 6(2), 65–70.
"""

import numpy as np
from scipy.stats import MonteCarloMethod, chi2_contingency


def independence_test(table, *, seed=20261013, resamples=99999) -> dict:
    """Pearson-Test; bei kleinen erwarteten Zellen reproduzierbares Monte Carlo.

    Leere Randkategorien werden vor dem Test entfernt. Der p-Wert setzt weiterhin
    ein geeignetes Unabhängigkeitsmodell voraus; Simulation löst keine zeitlichen
    Abhängigkeiten. Cramérs V wird aus derselben Pearson-Statistik berechnet.
    """
    values = np.asarray(table, dtype=float)
    if values.ndim != 2 or not np.isfinite(values).all():
        raise ValueError("Erwartet wird eine endliche zweidimensionale Häufigkeitstabelle")
    if (values < 0).any() or (values != np.floor(values)).any():
        raise ValueError("Häufigkeiten müssen nicht negative ganze Zahlen sein")
    values = values[values.sum(axis=1) > 0][:, values.sum(axis=0) > 0].astype(np.int64)
    if min(values.shape) < 2:
        raise ValueError("Mindestens zwei besetzte Kategorien je Dimension erforderlich")
    result = chi2_contingency(values, correction=False)
    expected = result.expected_freq
    method = "Pearson chi-square (asymptotic)"
    p_value = float(result.pvalue)
    simulated = bool((expected < 5).any())
    if simulated:
        simulation = MonteCarloMethod(
            n_resamples=resamples, batch=1000, rng=np.random.default_rng(seed)
        )
        p_value = float(chi2_contingency(values, correction=False, method=simulation).pvalue)
        method = "Pearson chi-square (Monte Carlo, fixed margins)"
    n = int(values.sum())
    return {
        "n": n,
        "chi2": float(result.statistic),
        "df": int(result.dof),
        "p_value": p_value,
        "cramers_v": float(np.sqrt(result.statistic / (n * (min(values.shape) - 1)))),
        "expected_min": float(expected.min()),
        "expected_cells_lt5": int((expected < 5).sum()),
        "method": method,
        "seed": seed if simulated else None,
        "resamples": resamples if simulated else None,
        "expected_counts": expected.tolist(),
    }


def holm_adjust(p_values) -> np.ndarray:
    """Holm-Korrektur: sortieren, mit m-rang multiplizieren, kumulatives Maximum."""
    values = np.asarray(p_values, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("p-Werte müssen ein endlicher Vektor im Bereich 0–1 sein")
    order = np.argsort(values, kind="stable")
    corrected = np.minimum(1, np.maximum.accumulate(values[order] * np.arange(len(values), 0, -1)))
    output = np.empty_like(values)
    output[order] = corrected
    return output
