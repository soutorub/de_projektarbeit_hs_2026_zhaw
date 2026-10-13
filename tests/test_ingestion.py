"""Offline-Tests der Datensicherung, keine Anfragen an den öffentlichen Server."""

import csv
import json
from unittest.mock import patch

import pytest

from de_projekt import config, ingestion


def write_csv(path):
    columns = sorted(config.REQUIRED_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerow(["sample"] * len(columns))


@pytest.fixture
def snapshot(tmp_path):
    path = tmp_path / config.RAW_FILENAME
    write_csv(path)
    metadata = {"download_url": config.CSV_URL, **ingestion.inspect_csv(path)}
    (tmp_path / "source_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (tmp_path / "catalog_metadata.json").write_text(
        json.dumps({"success": True, "result": {}}), encoding="utf-8"
    )
    return tmp_path


def test_existing_snapshot_is_reused_without_network(snapshot):
    with patch.object(ingestion, "download", side_effect=AssertionError("Network used")):
        assert ingestion.run(snapshot) == snapshot / config.RAW_FILENAME


def test_tampered_snapshot_fails_without_redownload(snapshot):
    path = snapshot / config.RAW_FILENAME
    path.write_bytes(path.read_bytes().replace(b"sample", b"changed", 1))
    with (
        patch.object(ingestion, "download", side_effect=AssertionError("Network used")),
        pytest.raises(ValueError, match="sha256"),
    ):
        ingestion.run(snapshot)


def test_incomplete_snapshot_is_rejected(tmp_path):
    write_csv(tmp_path / config.RAW_FILENAME)
    with (
        patch.object(ingestion, "download", side_effect=AssertionError("Network used")),
        pytest.raises(FileNotFoundError),
    ):
        ingestion.run(tmp_path)


def test_missing_columns_are_rejected(tmp_path):
    path = tmp_path / "invalid.csv"
    path.write_text("AccidentUID\n123\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Pflichtspalten"):
        ingestion.inspect_csv(path)


def test_failed_refresh_preserves_original_and_cleans_staging(snapshot):
    original = (snapshot / config.RAW_FILENAME).read_bytes()
    with (
        patch.object(ingestion, "download", side_effect=OSError("Download failed")),
        pytest.raises(OSError, match="Download failed"),
    ):
        ingestion.run(snapshot, refresh=True)
    assert (snapshot / config.RAW_FILENAME).read_bytes() == original
    assert list((snapshot / "snapshots").iterdir()) == []


def test_refresh_publishes_separate_valid_snapshot(snapshot):
    original = (snapshot / config.RAW_FILENAME).read_bytes()

    def fake_download(url, destination):
        if url == config.CSV_URL:
            write_csv(destination)
        else:
            destination.write_text('{"success": true, "result": {}}', encoding="utf-8")

    with patch.object(ingestion, "download", side_effect=fake_download):
        new_path = ingestion.run(snapshot, refresh=True)
    assert new_path.parent.parent == snapshot / "snapshots"
    assert ingestion.validate_snapshot(new_path.parent) == new_path
    assert (snapshot / config.RAW_FILENAME).read_bytes() == original


def test_empty_and_malformed_csv_are_rejected(tmp_path):
    path = tmp_path / "invalid.csv"
    columns = sorted(config.REQUIRED_COLUMNS)
    path.write_text(",".join(columns) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="keine Datenzeilen"):
        ingestion.inspect_csv(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("too,few\n")
    with pytest.raises(ValueError, match="Spaltenzahl"):
        ingestion.inspect_csv(path)


def test_invalid_catalog_does_not_publish_snapshot(snapshot):
    def fake_download(url, destination):
        if url == config.CSV_URL:
            write_csv(destination)
        else:
            destination.write_text('{"success": false}', encoding="utf-8")

    with (
        patch.object(ingestion, "download", side_effect=fake_download),
        pytest.raises(ValueError, match="Katalogantwort"),
    ):
        ingestion.run(snapshot, refresh=True)
    assert list((snapshot / "snapshots").iterdir()) == []


def test_download_detects_truncated_response(tmp_path):
    from io import BytesIO

    response = BytesIO(b"partial")
    response.headers = {"Content-Length": "100"}
    with (
        patch.object(ingestion, "urlopen", return_value=response),
        pytest.raises(ValueError, match="Unvollständiger Download"),
    ):
        ingestion.download(config.CSV_URL, tmp_path / "partial.csv")
