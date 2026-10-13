"""Fachliche Regeln und Erhalt unbekannter Angaben mit kleinen Beispielen prüfen."""

import pandas as pd
import pytest

from de_projekt import transformation


def example_rows(count=1):
    row = {
        "AccidentUID": "0" * 32,
        "AccidentYear": "2025",
        "AccidentMonth": "1",
        "AccidentWeekDay": "aw401",
        "AccidentWeekDay_de": "Montag",
        "AccidentHour": "0",
        "AccidentType": "at0",
        "AccidentType_de": "Schleuder- oder Selbstunfall",
        "AccidentSeverityCategory": "as4",
        "AccidentSeverityCategory_de": "Unfall mit Sachschaden",
        "RoadType": "rt433",
        "RoadType_de": "Nebenstrasse",
        "CantonCode": "ZH",
        "MunicipalityCode": "0261",
        "AccidentLocation_CHLV95_E": "2680000",
        "AccidentLocation_CHLV95_N": "1248000",
        "AccidentInvolvingPedestrian": "false",
        "AccidentInvolvingBicycle": "false",
        "AccidentInvolvingMotorcycle": "true",
    }
    return pd.DataFrame([{**row, "AccidentUID": f"{i:032X}"} for i in range(count)], dtype="string")


def test_time_period_boundaries_and_weekend():
    raw = example_rows(8)
    raw["AccidentHour"] = ["0", "5", "6", "11", "12", "17", "18", "23"]
    raw["AccidentWeekDay"] = ["aw401", "aw405", "aw406", "aw407"] * 2
    clean, report = transformation.transform(raw)
    assert clean["time_period"].tolist() == [
        "night",
        "night",
        "morning",
        "morning",
        "afternoon",
        "afternoon",
        "evening",
        "evening",
    ]
    assert clean["is_weekend"].tolist() == [False, False, True, True] * 2
    assert report["rows_excluded"] == 0


def test_three_valued_participation_and_missing_time():
    raw = example_rows(6)
    raw["AccidentInvolvingPedestrian"] = ["true", "false", "", "", "false", "true"]
    raw["AccidentInvolvingBicycle"] = ["", "false", "true", "", "", "true"]
    raw.loc[0, ["AccidentWeekDay", "AccidentHour"]] = ""
    clean, _ = transformation.transform(raw)
    expected = pd.Series([True, False, True, pd.NA, pd.NA, True], dtype="boolean")
    pd.testing.assert_series_equal(clean["vulnerable_road_user"], expected, check_names=False)
    assert pd.isna(clean.loc[0, "is_weekend"])
    assert pd.isna(clean.loc[0, "time_period"])


@pytest.mark.parametrize(
    "column,value",
    [
        ("AccidentHour", "24"),
        ("AccidentHour", "1.5"),
        ("AccidentMonth", "0"),
        ("AccidentYear", "text"),
        ("AccidentWeekDay", "aw999"),
        ("AccidentSeverityCategory", "as99"),
        ("AccidentInvolvingBicycle", "unknown"),
        ("AccidentLocation_CHLV95_E", "inf"),
        ("AccidentUID", ""),
    ],
)
def test_invalid_values_fail_instead_of_disappearing(column, value):
    raw = example_rows()
    raw.loc[0, column] = value
    with pytest.raises(ValueError):
        transformation.transform(raw)


def test_duplicate_ids_fail():
    raw = example_rows(2)
    raw.loc[1, "AccidentUID"] = raw.loc[0, "AccidentUID"]
    with pytest.raises(ValueError, match="eindeutig"):
        transformation.transform(raw)


def test_preserves_raw_and_property_damage_and_code_zero():
    raw = example_rows()
    raw["unneeded_language"] = "original"
    raw.loc[0, "AccidentInvolvingBicycle"] = "true"
    raw.loc[0, "AccidentMonth"] = " 1 "
    original = raw.copy(deep=True)
    clean, report = transformation.transform(raw)
    pd.testing.assert_frame_equal(raw, original)
    assert len(clean) == 1
    assert clean.loc[0, "AccidentSeverityCategory"] == "as4"
    assert clean.loc[0, "MunicipalityCode"] == "0261"
    assert clean.loc[0, "vulnerable_road_user"]
    assert report["trimmed_values"]["AccidentMonth"] == 1
    assert report["dropped_columns"] == ["unneeded_language"]


def test_csv_round_trip_preserves_nullable_types(tmp_path):
    raw = example_rows(2)
    raw.loc[0, ["AccidentInvolvingBicycle", "AccidentInvolvingPedestrian", "AccidentHour"]] = ""
    clean, _ = transformation.transform(raw)
    export = clean.copy()
    for column in (*transformation.PARTICIPATION, "is_weekend", "vulnerable_road_user"):
        export[column] = export[column].astype("Int64")
    path = tmp_path / "clean.csv"
    export.to_csv(path, index=False)
    pd.testing.assert_frame_equal(clean, transformation.read_clean(path))
