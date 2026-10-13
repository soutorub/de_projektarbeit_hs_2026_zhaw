"""Unveränderte Raw-Snapshots beschaffen und offline prüfen.

Quelle: https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte
(Bundesamt für Strassen ASTRA). Keine Bereinigung in dieser Phase.
"""

import argparse
import csv
import hashlib
import json
import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

from de_projekt import config

LOGGER = logging.getLogger(__name__)


def inspect_csv(path: Path) -> dict:
    """CSV-Struktur und Pflichtspalten prüfen; Inhalt unverändert lassen."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        columns = next(reader, [])
        missing = config.REQUIRED_COLUMNS.difference(columns)
        if missing:
            raise ValueError(f"Fehlende Pflichtspalten: {', '.join(sorted(missing))}")
        if len(columns) != len(set(columns)):
            raise ValueError("Doppelte Spaltennamen")
        count = 0
        for line, row in enumerate(reader, start=2):
            if len(row) != len(columns):
                raise ValueError(f"Ungültige Spaltenzahl in CSV-Datensatz {line}")
            count += 1
        if not count:
            raise ValueError("CSV enthält keine Datenzeilen")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "rows": count,
        "columns": columns,
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest().upper(),
    }


def validate_snapshot(directory: Path) -> Path:
    """Daten und Metadaten müssen vor einer Wiederverwendung übereinstimmen."""
    path = directory / config.RAW_FILENAME
    metadata = json.loads((directory / "source_metadata.json").read_text(encoding="utf-8-sig"))
    actual = inspect_csv(path)
    for key in ("sha256", "bytes", "rows", "columns"):
        if metadata.get(key) != actual[key]:
            raise ValueError(f"Snapshot stimmt nicht mit Metadaten überein: {key}")
    if metadata.get("download_url") != config.CSV_URL:
        raise ValueError("Unerwartete Download-Quelle")
    catalog = json.loads((directory / "catalog_metadata.json").read_text(encoding="utf-8-sig"))
    if catalog.get("success") is not True or not isinstance(catalog.get("result"), dict):
        raise ValueError("Ungültige Katalogantwort")
    LOGGER.info("Snapshot geprüft: %s (%s Zeilen)", path, actual["rows"])
    return path


def download(url: str, destination: Path) -> None:
    """HTTP-Fehler durchreichen und angekündigte Download-Grösse prüfen."""
    with urlopen(url, timeout=60) as response, destination.open("wb") as handle:
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            handle.write(chunk)
        expected = response.headers.get("Content-Length")
    if expected is not None and destination.stat().st_size != int(expected):
        raise ValueError(f"Unvollständiger Download: {url}")


def run(raw_dir: Path | None = None, *, refresh: bool = False) -> Path:
    """Lokalen Snapshot nutzen; neue Downloads in separaten Verzeichnissen sichern.

    Der zurückgegebene CSV-Pfad ist die Schnittstelle zur Transformation.
    Nach einem Download wird sein Verzeichnis explizit als raw_dir ausgewählt.
    """
    directory = Path(raw_dir) if raw_dir is not None else config.RAW_DIR
    names = (config.RAW_FILENAME, "source_metadata.json", "catalog_metadata.json")
    if not refresh and any((directory / name).exists() for name in names):
        # Defekte Snapshots nicht still durch einen anderen Datenstand ersetzen.
        return validate_snapshot(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    target = directory / "snapshots" / stamp
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ingestion-", dir=target.parent) as temporary:
        staging = Path(temporary) / "snapshot"
        staging.mkdir()
        download(config.CSV_URL, staging / config.RAW_FILENAME)
        download(config.CATALOG_URL, staging / "catalog_metadata.json")
        metadata = {
            "retrieved_at": datetime.now(UTC).isoformat(),
            "source_url": config.SOURCE_URL,
            "download_url": config.CSV_URL,
            "file_name": config.RAW_FILENAME,
            **inspect_csv(staging / config.RAW_FILENAME),
        }
        (staging / "source_metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        validate_snapshot(staging)
        staging.rename(target)
    LOGGER.info("Neuer Snapshot: %s; künftig mit --raw-dir auswählen", target)
    return target / config.RAW_FILENAME


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=config.RAW_DIR)
    parser.add_argument("--refresh", action="store_true", help="Separaten Snapshot herunterladen")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        path = run(args.raw_dir, refresh=args.refresh)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f"Ingestion fehlgeschlagen: {error}\n")
    print(path)


if __name__ == "__main__":
    main()
