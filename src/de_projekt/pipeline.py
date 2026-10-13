"""Teil-1-Batch-Pipeline: ausgewählter Snapshot → Transformation → SQLite."""

import argparse
import sqlite3
from pathlib import Path

from de_projekt import config, ingestion, storage, transformation


def run(raw_dir: Path | None = None, output_dir: Path | None = None) -> Path:
    """Explizite Pfadübergabe verhindert die Mischung verschiedener Datenstände."""
    raw_path = ingestion.run(raw_dir)
    clean_path = transformation.run(raw_path, output_dir)
    return storage.run(clean_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=config.RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=config.PROCESSED_DIR)
    args = parser.parse_args()
    try:
        path = run(args.raw_dir, args.output_dir)
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        parser.exit(1, f"Pipeline fehlgeschlagen: {error}\n")
    print(path)


if __name__ == "__main__":
    main()
