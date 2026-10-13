"""Validierung, explizite Datentypen und nachvollziehbare Analysemerkmale.

Grundlage: notebooks/01_datenprofil.ipynb und README (Bereinigungsentscheidungen).
Felddefinitionen: https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte
(Bundesamt für Strassen ASTRA). Rohdaten und gültige Zeilen bleiben erhalten.
"""

import argparse
import hashlib
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from de_projekt import config, ingestion

PARTICIPATION = (
    "AccidentInvolvingPedestrian",
    "AccidentInvolvingBicycle",
    "AccidentInvolvingMotorcycle",
)
CODE_VALUES = {
    "AccidentType": {"at00", *(f"at{i}" for i in range(10))},
    "AccidentSeverityCategory": {"as1", "as2", "as3", "as4"},
    "RoadType": {f"rt{i}" for i in range(430, 440)},
    "AccidentWeekDay": {f"aw{i}" for i in range(401, 408)},
}
SELECTED_COLUMNS = (
    "AccidentUID",
    "AccidentYear",
    "AccidentMonth",
    "AccidentWeekDay",
    "AccidentHour",
    "AccidentType",
    "AccidentType_de",
    "AccidentSeverityCategory",
    "AccidentSeverityCategory_de",
    "RoadType",
    "RoadType_de",
    "AccidentWeekDay_de",
    *PARTICIPATION,
    "AccidentLocation_CHLV95_E",
    "AccidentLocation_CHLV95_N",
    "CantonCode",
    "MunicipalityCode",
)
RULE_VERSION = "1.0"


def transform(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Unbekannte Angaben erhalten; ungültige nicht leere Werte sichtbar ablehnen.

    Keine Imputation, Deduplizierung oder Einschränkung auf Personenschäden.
    Die H2-Teilmenge wird erst bei der Analyse ausgewählt.
    """
    missing_columns = set(SELECTED_COLUMNS).difference(raw.columns)
    if missing_columns:
        raise ValueError(f"Fehlende Transformationsspalten: {sorted(missing_columns)}")
    if raw.empty or not raw.columns.is_unique:
        raise ValueError("Leere Datenbasis oder doppelte Spaltennamen")
    original = raw.loc[:, SELECTED_COLUMNS].astype("string")
    stripped = original.apply(lambda column: column.str.strip())
    trimmed = original.ne(stripped).sum().astype(int).to_dict()
    clean = stripped.replace("", pd.NA)
    uid = clean["AccidentUID"]
    if uid.isna().any() or uid.duplicated().any():
        raise ValueError("Unfall-IDs müssen vorhanden und eindeutig sein")
    if not uid.str.fullmatch(r"[0-9A-Fa-f]{32}").all():
        raise ValueError("Ungültiges Unfall-ID-Format")

    for column, allowed in CODE_VALUES.items():
        invalid = clean[column].notna() & ~clean[column].isin(allowed)
        if invalid.any():
            raise ValueError(f"Ungültige Codes in {column}: {clean.loc[invalid, column].unique()}")

    limits = {"AccidentYear": (2011, 9999), "AccidentMonth": (1, 12), "AccidentHour": (0, 23)}
    for column, (low, high) in limits.items():
        values = pd.to_numeric(clean[column], errors="coerce")
        invalid = clean[column].notna() & (
            values.isna() | ~values.between(low, high) | values.mod(1).ne(0)
        )
        if invalid.any():
            raise ValueError(f"Ungültige Ganzzahl oder Wertebereich in {column}")
        clean[column] = values.astype("Int64")
    for column in ("AccidentLocation_CHLV95_E", "AccidentLocation_CHLV95_N"):
        values = pd.to_numeric(clean[column], errors="coerce").astype("Float64")
        if (clean[column].notna() & (values.isna() | ~np.isfinite(values))).any():
            raise ValueError(f"Ungültige numerische Koordinate in {column}")
        clean[column] = values
    for column in PARTICIPATION:
        if (clean[column].notna() & ~clean[column].isin(["true", "false"])).any():
            raise ValueError(f"Ungültiger Beteiligungswert in {column}")
        clean[column] = clean[column].map({"true": True, "false": False}).astype("boolean")

    # Null-Masken verhindern, dass unbekannte Eingaben als negative Aussage gelten.
    clean["is_weekend"] = clean["AccidentWeekDay"].isin(["aw406", "aw407"]).astype("boolean")
    clean.loc[clean["AccidentWeekDay"].isna(), "is_weekend"] = pd.NA
    clean["time_period"] = pd.cut(
        clean["AccidentHour"].astype("Float64"),
        bins=[-1, 5, 11, 17, 23],
        labels=["night", "morning", "afternoon", "evening"],
    ).astype("string")
    clean["vulnerable_road_user"] = (
        clean["AccidentInvolvingPedestrian"] | clean["AccidentInvolvingBicycle"]
    )
    details = {
        "rule_version": RULE_VERSION,
        "rows_before": len(raw),
        "rows_after": len(clean),
        "rows_excluded": 0,
        "columns_before": len(raw.columns),
        "columns_after": len(clean.columns),
        "dropped_columns": [column for column in raw.columns if column not in SELECTED_COLUMNS],
        "trimmed_values": trimmed,
        "missing_before": original.isna().sum().add(original.eq("").sum()).astype(int).to_dict(),
        "missing_after": clean.isna().sum().astype(int).to_dict(),
        "output_dtypes": clean.dtypes.astype(str).to_dict(),
        "feature_definitions": {
            "is_weekend": "aw406/aw407; unbekannter Wochentag bleibt unbekannt",
            "time_period": "night 00–05; morning 06–11; afternoon 12–17; evening 18–23",
            "vulnerable_road_user": "Fussgänger ODER Velo; nullable boolesche ODER-Verknüpfung",
        },
        "limitations": [
            "Beteiligungssemantik weicht von Katalogbeschreibung ab; Werte erhalten",
            "Sachschaden-Erfassungswechsel Juli 2015; keine automatische Korrektur",
            "Numerische Koordinatenprüfung ist keine Stadtgrenzenprüfung",
        ],
    }
    return clean, details


def read_clean(path: Path) -> pd.DataFrame:
    """CSV-Datentypen für spätere Speicherung reproduzierbar wiederherstellen."""
    types = {column: "string" for column in SELECTED_COLUMNS}
    types.update({column: "Int64" for column in ("AccidentYear", "AccidentMonth", "AccidentHour")})
    types.update(
        {column: "Float64" for column in ("AccidentLocation_CHLV95_E", "AccidentLocation_CHLV95_N")}
    )
    types.update(
        {column: "boolean" for column in (*PARTICIPATION, "is_weekend", "vulnerable_road_user")}
    )
    types["time_period"] = "string"
    return pd.read_csv(path, dtype=types, keep_default_na=False, na_values=[""])


def run(raw_path: Path | None = None, output_dir: Path | None = None) -> Path:
    """Ausgewählten lokalen Snapshot validieren und abgeleitete Artefakte schreiben."""
    path = Path(raw_path) if raw_path is not None else config.RAW_DIR / config.RAW_FILENAME
    if path.name != config.RAW_FILENAME:
        raise ValueError("Erwartet wird die CSV eines validierten Raw-Snapshots")
    ingestion.validate_snapshot(path.parent)
    raw = pd.read_csv(path, dtype="string", keep_default_na=False, encoding="utf-8-sig")
    clean, report = transform(raw)
    source = json.loads((path.parent / "source_metadata.json").read_text(encoding="utf-8-sig"))
    report.update(
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "source_sha256": source["sha256"],
            "source_url": config.SOURCE_URL,
            "versions": {"pandas": pd.__version__, "numpy": np.__version__},
        }
    )
    directory = Path(output_dir) if output_dir is not None else config.PROCESSED_DIR
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".transformation-", dir=directory) as temporary:
        staging = Path(temporary)
        csv_path = staging / config.CLEAN_FILENAME
        # Im Export 0/1 statt sprachabhängiger boolescher Texte; Leerwert bedeutet unbekannt.
        export = clean.copy()
        for column in (*PARTICIPATION, "is_weekend", "vulnerable_road_user"):
            export[column] = export[column].astype("Int64")
        export.to_csv(csv_path, index=False, encoding="utf-8", lineterminator="\n")
        pd.testing.assert_frame_equal(clean, read_clean(csv_path))
        report["output_sha256"] = hashlib.sha256(csv_path.read_bytes()).hexdigest().upper()
        report_path = staging / config.QUALITY_FILENAME
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        # Jeder Austausch ist atomar; die Prüfsumme bindet Bericht und CSV zusammen.
        csv_path.replace(directory / config.CLEAN_FILENAME)
        report_path.replace(directory / config.QUALITY_FILENAME)
    ingestion.validate_snapshot(path.parent)
    return directory / config.CLEAN_FILENAME


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=config.RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=config.PROCESSED_DIR)
    args = parser.parse_args()
    try:
        path = run(args.raw_dir / config.RAW_FILENAME, args.output_dir)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Transformation fehlgeschlagen: {error}\n")
    print(path)


if __name__ == "__main__":
    main()
