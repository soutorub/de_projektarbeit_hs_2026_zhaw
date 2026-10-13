"""Bereinigte Daten mit explizitem Schema in einer portablen SQLite-Datei sichern."""

import argparse
import hashlib
import json
import sqlite3
import tempfile
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

import numpy as np
import pandas as pd

from de_projekt import config, transformation


def run(clean_path: Path | None = None, database_path: Path | None = None) -> Path:
    """CSV und Qualitätsbericht prüfen, neue DB aufbauen, erst danach veröffentlichen.

    Kein Anhängen: Wiederholungen erzeugen denselben Unfallbestand. Bei Fehlern
    bleibt eine bereits vorhandene Datenbank erhalten. Die SQLite-Verbindung wird
    vor dem Austausch geschlossen (wichtig auch unter Windows).
    """
    if sqlite3.sqlite_version_info < (3, 37, 0):
        raise RuntimeError("Das STRICT-Schema benötigt SQLite >= 3.37")
    path = (
        Path(clean_path) if clean_path is not None else config.PROCESSED_DIR / config.CLEAN_FILENAME
    )
    target = (
        Path(database_path) if database_path is not None else path.parent / config.DATABASE_FILENAME
    )
    if target.resolve() in {path.resolve(), (path.parent / config.QUALITY_FILENAME).resolve()}:
        raise ValueError("Datenbankziel darf keine Eingabedatei überschreiben")
    report = json.loads((path.parent / config.QUALITY_FILENAME).read_text(encoding="utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if report.get("output_sha256") != digest:
        raise ValueError("CSV-Prüfsumme passt nicht zum Qualitätsbericht")
    if report.get("rule_version") != transformation.RULE_VERSION:
        raise ValueError("Unbekannte Transformationsregelversion")
    clean = transformation.read_clean(path)
    expected_columns = [
        *transformation.SELECTED_COLUMNS,
        "is_weekend",
        "time_period",
        "vulnerable_road_user",
    ]
    if list(clean.columns) != expected_columns or len(clean) != report.get("rows_after"):
        raise ValueError("Spalten oder Zeilenzahl passen nicht zum vereinbarten Datenbestand")
    if clean.empty:
        raise ValueError("Leerer Unfallbestand")
    schema = files("de_projekt").joinpath("schema.sql").read_text(encoding="utf-8")
    metadata = {
        "schema_version": "1.0",
        "source_sha256": report["source_sha256"],
        "clean_sha256": digest,
        "rule_version": report["rule_version"],
        "quality_report_sha256": hashlib.sha256(
            (path.parent / config.QUALITY_FILENAME).read_bytes()
        )
        .hexdigest()
        .upper(),
        "source_url": report["source_url"],
        "rows": str(len(clean)),
        "sqlite_version": sqlite3.sqlite_version,
        "created_at": datetime.now(UTC).isoformat(),
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".storage-", dir=target.parent) as temporary:
        staged = Path(temporary) / config.DATABASE_FILENAME
        connection = sqlite3.connect(staged)
        try:
            connection.executescript("BEGIN;\n" + schema)
            # Nur interne Spaltennamen; Werte werden als SQL-Parameter übergeben.
            columns = ", ".join(f'"{column}"' for column in expected_columns)
            placeholders = ", ".join("?" for _ in expected_columns)
            records = (
                tuple(
                    None
                    if pd.isna(value)
                    else value.item()
                    if isinstance(value, np.generic)
                    else value
                    for value in row
                )
                for row in clean.itertuples(index=False, name=None)
            )
            connection.executemany(
                f"INSERT INTO accidents ({columns}) VALUES ({placeholders})", records
            )
            connection.executemany("INSERT INTO pipeline_metadata VALUES (?, ?)", metadata.items())
            # Alle Werte vergleichen, nicht nur Zeilenzahlen; NULL und Typen einschliessen.
            restored = pd.read_sql_query("SELECT * FROM accidents ORDER BY AccidentUID", connection)
            restored = restored.astype(clean.dtypes.to_dict())
            expected = clean.sort_values("AccidentUID").reset_index(drop=True)
            pd.testing.assert_frame_equal(expected, restored)
            if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise ValueError("SQLite-Integritätsprüfung fehlgeschlagen")
            connection.commit()
        finally:
            connection.close()
        staged.replace(target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=config.PROCESSED_DIR)
    args = parser.parse_args()
    try:
        path = run(args.processed_dir / config.CLEAN_FILENAME)
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        parser.exit(1, f"Storage fehlgeschlagen: {error}\n")
    print(path)


if __name__ == "__main__":
    main()
