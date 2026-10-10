# de_projektarbeit_hs_2026_zhaw

Projektarbeit für das Modul Data Engineering (ZHAW, HS26).

## Team

- Ruben Souto
- Issa Fawaz
- Drin Muslija

## Struktur

```
src/de_projekt/   Pipeline-Code (ingestion, storage, transformation, serving)
notebooks/        Analysen und Hypothesentests
data/raw/         Rohdaten
data/processed/   Aufbereitete Daten
presentations/    Präsentationsdateien der Kolloquien
tests/            Tests
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Verwendung

```bash
python -m de_projekt.pipeline   # Pipeline ausführen
pytest                          # Tests
ruff check .                    # Linting
```

## Abgabe

Code, Daten und Präsentationsdateien werden über den Abgabe-Branch eingereicht:

- Teil 1: 27. Oktober 2026, 23:59 Uhr
- Teil 2: 8. Dezember 2026, 23:59 Uhr

Externe Quellen (Literatur, Code-Vorlagen) werden als Kommentar im Code gemäss
ZHAW-Zitierleitfaden angegeben.
