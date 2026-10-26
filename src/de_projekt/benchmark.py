"""Skalierungstest: dieselbe Pipeline mit vervielfachtem Snapshot messen.

Der echte Snapshot wird k-fach kopiert; Kopien erhalten neue, eindeutige Unfall-IDs.
Ingestion, Transformation und Storage laufen unverändert in einem temporären
Verzeichnis. Der Testsnapshot entsteht vorab; jede Messung läuft in einem eigenen
Prozess, damit der Spitzenspeicher nur die Pipeline selbst abbildet. Raw und processed bleiben
unberührt; nur die Messtabelle wird geschrieben.
"""

import argparse
import hashlib
import json
import platform
import resource
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd

from de_projekt import config, ingestion, storage, transformation

RESULT_FILENAME = "scaling_benchmark.csv"


def replicate(raw: pd.DataFrame, factor: int) -> pd.DataFrame:
    """Kopie 0 bleibt original; weitere Kopien erhalten MD5-basierte 32-Hex-IDs."""
    copies = [raw]
    for copy in range(1, factor):
        extra = raw.copy()
        extra["AccidentUID"] = [
            hashlib.md5(f"{copy}:{uid}".encode()).hexdigest().upper() for uid in raw["AccidentUID"]
        ]
        copies.append(extra)
    return pd.concat(copies, ignore_index=True)


def peak_memory_mb() -> float:
    """ru_maxrss ist unter macOS in Bytes, unter Linux in Kilobytes."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / 1024**2 if sys.platform == "darwin" else peak / 1024


def build_snapshot(factor: int, raw_dir: Path) -> dict:
    """Vervielfachten Snapshot samt Metadaten wie bei einem echten Download ablegen."""
    raw_dir.mkdir(parents=True)
    raw = pd.read_csv(
        config.RAW_DIR / config.RAW_FILENAME,
        dtype="string",
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    replicate(raw, factor).to_csv(raw_dir / config.RAW_FILENAME, index=False, encoding="utf-8")
    metadata = {
        "source_url": config.SOURCE_URL,
        "download_url": config.CSV_URL,
        "file_name": config.RAW_FILENAME,
        **ingestion.inspect_csv(raw_dir / config.RAW_FILENAME),
    }
    (raw_dir / "source_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    shutil.copy(config.RAW_DIR / "catalog_metadata.json", raw_dir)
    return metadata


def measure(factor: int, workdir: Path) -> dict:
    """Einen vorbereiteten Snapshot Phase für Phase durch die Pipeline führen."""
    raw_dir = workdir / "raw"
    metadata = json.loads((raw_dir / "source_metadata.json").read_text(encoding="utf-8"))
    timings = {}
    start = time.perf_counter()
    raw_path = ingestion.run(raw_dir)
    timings["ingestion_s"] = time.perf_counter() - start
    start = time.perf_counter()
    clean_path = transformation.run(raw_path, workdir / "processed")
    timings["transformation_s"] = time.perf_counter() - start
    start = time.perf_counter()
    database = storage.run(clean_path)
    timings["storage_s"] = time.perf_counter() - start
    # Typische Serving-Abfrage aus F3; misst Lesezugriff auf die fertige Datenbank.
    with sqlite3.connect(database) as connection:
        start = time.perf_counter()
        connection.execute(
            "SELECT AccidentYear, COUNT(*) FROM accidents GROUP BY AccidentYear"
        ).fetchall()
        timings["query_s"] = time.perf_counter() - start
    return {
        "factor": factor,
        "rows": metadata["rows"],
        "raw_mb": metadata["bytes"] / 1024**2,
        "sqlite_mb": database.stat().st_size / 1024**2,
        **timings,
        "total_s": sum(timings.values()),
        "peak_memory_mb": peak_memory_mb(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--factors", type=int, nargs="+", default=[1, 2, 5, 10])
    parser.add_argument("--output", type=Path, default=config.PROCESSED_DIR / RESULT_FILENAME)
    parser.add_argument("--single", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--workdir", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.single is not None:
        # Kindprozess: genau einen Faktor messen und als JSON an den Elternprozess geben.
        print(json.dumps(measure(args.single, args.workdir)))
        return
    results = []
    for factor in args.factors:
        with tempfile.TemporaryDirectory(prefix=".benchmark-") as temporary:
            build_snapshot(factor, Path(temporary) / "raw")
            command = [sys.executable, "-m", "de_projekt.benchmark"]
            command += ["--single", str(factor), "--workdir", temporary]
            output = subprocess.run(command, check=True, capture_output=True, text=True).stdout
        results.append(json.loads(output.strip().splitlines()[-1]))
        print(f"Faktor {factor}: {results[-1]['total_s']:.1f} s", flush=True)
    table = pd.DataFrame(results).round(3)
    table["platform"] = (
        f"{platform.system()} {platform.machine()}, Python {platform.python_version()}"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False, lineterminator="\n")
    print(table.drop(columns="platform").to_string(index=False))


if __name__ == "__main__":
    main()
