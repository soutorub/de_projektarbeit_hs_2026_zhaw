"""Datenbank-Constraints, NULL-Werte und Schutz bestehender Artefakte prüfen."""

import hashlib
import json
import sqlite3

import pandas as pd
import pytest

from de_projekt import config, pipeline, storage, transformation
from tests.test_transformation import example_rows


def prepare(tmp_path, raw=None):
    raw = example_rows(2) if raw is None else raw
    clean, report = transformation.transform(raw)
    export = clean.copy()
    for column in (*transformation.PARTICIPATION, "is_weekend", "vulnerable_road_user"):
        export[column] = export[column].astype("Int64")
    path = tmp_path / config.CLEAN_FILENAME
    export.to_csv(path, index=False)
    report.update(
        {
            "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
            "source_sha256": "A" * 64,
            "source_url": config.SOURCE_URL,
        }
    )
    (tmp_path / config.QUALITY_FILENAME).write_text(json.dumps(report), encoding="utf-8")
    return path


def test_storage_preserves_nulls_and_leading_zero(tmp_path):
    raw = example_rows(2)
    raw.loc[
        0,
        [
            "AccidentHour",
            "AccidentWeekDay",
            "AccidentInvolvingPedestrian",
            "AccidentInvolvingBicycle",
        ],
    ] = ""
    db = storage.run(prepare(tmp_path, raw))
    with sqlite3.connect(db) as connection:
        assert connection.execute(
            "SELECT AccidentHour, is_weekend, vulnerable_road_user, MunicipalityCode "
            "FROM accidents ORDER BY AccidentUID LIMIT 1"
        ).fetchone() == (None, None, None, "0261")
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute(
            "SELECT value FROM pipeline_metadata WHERE key='rows'"
        ).fetchone() == ("2",)


@pytest.mark.parametrize(
    "assignment",
    [
        "AccidentHour = 24",
        "AccidentInvolvingBicycle = 2",
        "is_weekend = 1",
        "time_period = 'evening'",
        "vulnerable_road_user = 1",
        "is_weekend = NULL",
        "AccidentYear = 'not a number'",
        "AccidentUID = NULL",
    ],
)
def test_sql_constraints_reject_invalid_edits(tmp_path, assignment):
    db = storage.run(prepare(tmp_path))
    with sqlite3.connect(db) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(f"UPDATE accidents SET {assignment}")


def test_repeated_storage_does_not_append(tmp_path):
    path = prepare(tmp_path)
    db = storage.run(path)
    storage.run(path)
    with sqlite3.connect(db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM accidents").fetchone() == (2,)


def test_mismatched_report_preserves_existing_database(tmp_path):
    path = prepare(tmp_path)
    db = storage.run(path)
    original = db.read_bytes()
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Prüfsumme"):
        storage.run(path)
    assert db.read_bytes() == original


def test_constraint_failure_does_not_replace_database(tmp_path):
    path = prepare(tmp_path)
    db = storage.run(path)
    original = db.read_bytes()
    # Auch bei passender CSV-Prüfsumme muss das SQL-Schema ungültige Werte stoppen.
    csv = pd.read_csv(path, dtype="string", keep_default_na=False)
    csv.loc[0, "AccidentHour"] = "24"
    csv.to_csv(path, index=False)
    report_path = tmp_path / config.QUALITY_FILENAME
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["output_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    report_path.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(sqlite3.IntegrityError):
        storage.run(path)
    assert db.read_bytes() == original
    assert not list(tmp_path.glob(".storage-*"))


def test_pipeline_passes_selected_paths(tmp_path, monkeypatch):
    raw_dir, output_dir = tmp_path / "raw", tmp_path / "processed"
    raw_path = raw_dir / config.RAW_FILENAME
    clean_path = output_dir / config.CLEAN_FILENAME
    calls = []

    def ingest(directory):
        calls.append(("ingestion", directory))
        return raw_path

    def transform(path, directory):
        calls.append(("transformation", path, directory))
        return clean_path

    def store(path):
        calls.append(("storage", path))
        return output_dir / config.DATABASE_FILENAME

    monkeypatch.setattr(pipeline.ingestion, "run", ingest)
    monkeypatch.setattr(pipeline.transformation, "run", transform)
    monkeypatch.setattr(pipeline.storage, "run", store)
    assert pipeline.run(raw_dir, output_dir) == output_dir / config.DATABASE_FILENAME
    assert calls == [
        ("ingestion", raw_dir),
        ("transformation", raw_path, output_dir),
        ("storage", clean_path),
    ]
