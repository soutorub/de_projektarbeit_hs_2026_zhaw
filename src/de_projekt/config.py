"""Zentrale Pfade und Einstellungen."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CLEAN_FILENAME = "accidents_clean.csv"
QUALITY_FILENAME = "quality_report.json"
DATABASE_FILENAME = "accidents.sqlite"

SOURCE_URL = "https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte"
CSV_URL = f"{SOURCE_URL}/download/RoadTrafficAccidentLocations.csv"
CATALOG_URL = (
    "https://data.stadt-zuerich.ch/api/3/action/package_show?id=sid_dav_strassenverkehrsunfallorte"
)
RAW_FILENAME = "RoadTrafficAccidentLocations.csv"
REQUIRED_COLUMNS = frozenset(
    {
        "AccidentUID",
        "AccidentYear",
        "AccidentMonth",
        "AccidentWeekDay",
        "AccidentHour",
        "AccidentSeverityCategory",
        "AccidentType",
        "RoadType",
        "AccidentInvolvingPedestrian",
        "AccidentInvolvingBicycle",
        "AccidentInvolvingMotorcycle",
        "AccidentLocation_CHLV95_E",
        "AccidentLocation_CHLV95_N",
    }
)
