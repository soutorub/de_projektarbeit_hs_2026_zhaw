"""Vervielfachte Testdaten müssen dieselben Regeln wie der echte Snapshot erfüllen."""

import pytest

from de_projekt import benchmark, transformation
from tests.test_transformation import example_rows


def test_replicate_keeps_original_and_creates_valid_unique_ids():
    raw = example_rows(2)
    replicated = benchmark.replicate(raw, 3)
    assert len(replicated) == 6
    assert replicated["AccidentUID"].is_unique
    assert replicated["AccidentUID"].head(2).tolist() == raw["AccidentUID"].tolist()
    # Die Transformation lehnt ungültige oder doppelte IDs ab; hier muss sie durchlaufen.
    clean, report = transformation.transform(replicated)
    assert report["rows_after"] == len(clean) == 6


def test_memory_measurement_reports_unsupported_platform(monkeypatch):
    """Fehlendes Unix-Modul darf den Paketimport nicht verhindern."""
    monkeypatch.setattr(benchmark, "resource", None)
    with pytest.raises(RuntimeError, match="macOS und Linux"):
        benchmark.peak_memory_mb()
