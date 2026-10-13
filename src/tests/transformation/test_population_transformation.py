from ndi.transformation.transform_population import (
    classify_row,
    load_local_governments,
    validate_output,
)
import ndi.transformation.transform_population as population_transform
import csv
def test_classify_national_record():
  row = {"prov":"0", "dist":"0", "gapa":"0"}
  assert classify_row(row) == "national"

def test_classify_province_record():
  row = {"prov":"1", "dist":"0", "gapa":"0"}
  assert classify_row(row) == "province"

def test_classify_district_record():
  row = {"prov":"1", "dist":"1", "gapa":0}
  assert classify_row(row) == "district"

def test_classify_local_government_record():
  row = {"prov":"1", "dist":"1", "gapa":1}
  assert classify_row(row) == "local_government"

def test_classify_institutional_record():
  row = {"prov":"1", "dist":"1", "gapa":"99"}
  assert classify_row(row) == "institutional"


def test_load_local_governments_selects_and_transforms_records(
    tmp_path, monkeypatch
):
    columns = [
        "prov", "dist", "gapa",
        "provname", "dname", "gapaname",
        "nHhld", "total", "male", "female",
    ]

    rows = [
        {
            "prov": "0", "dist": "0", "gapa": "0",
            "provname": "Nepal", "dname": "", "gapaname": "",
            "nHhld": "100", "total": "500", "male": "250",
            "female": "250",
        },
        {
            "prov": "1", "dist": "0", "gapa": "0",
            "provname": "Koshi", "dname": "", "gapaname": "",
            "nHhld": "100", "total": "500", "male": "250",
            "female": "250",
        },
        {
            "prov": "1", "dist": "1", "gapa": "0",
            "provname": "Koshi", "dname": "District A",
            "gapaname": "", "nHhld": "100", "total": "500",
            "male": "250", "female": "250",
        },
        {
            "prov": "1", "dist": "1", "gapa": "1",
            "provname": "Koshi", "dname": "District A",
            "gapaname": "Municipality A", "nHhld": "120",
            "total": "600", "male": "310", "female": "290",
        },
        {
            "prov": "1", "dist": "1", "gapa": "99",
            "provname": "Koshi", "dname": "District A",
            "gapaname": "Institutional", "nHhld": "10",
            "total": "40", "male": "25", "female": "15",
        },
    ]

    sample_file = tmp_path / "sample_population.csv"

    with sample_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    monkeypatch.setattr(
        population_transform, "RAW_FILE", sample_file
    )

    records = load_local_governments()

    assert len(records) == 1

    record = records[0]

    assert record["local_government_name"] == "Municipality A"
    assert record["province_code"] == 1
    assert record["district_code"] == 1
    assert record["local_government_code"] == 1
    assert record["households"] == 120
    assert record["population_total"] == 600
    assert record["population_male"] == 310
    assert record["population_female"] == 290


def test_load_local_governments_rejects_missing_columns(
    tmp_path, monkeypatch
):
    sample_file = tmp_path / "missing_columns.csv"
    sample_file.write_text(
        "prov,dist,gapa\n1,1,1\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        population_transform, "RAW_FILE", sample_file
    )

    import pytest

    with pytest.raises(
        ValueError, match="Missing required columns"
    ):
        load_local_governments()


def test_load_local_governments_rejects_invalid_geographic_codes(
    tmp_path, monkeypatch
):
    columns = [
        "prov", "dist", "gapa",
        "provname", "dname", "gapaname",
        "nHhld", "total", "male", "female",
    ]

    sample_file = tmp_path / "invalid_geographic_codes.csv"

    with sample_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerow({
            "prov": "abc",
            "dist": "1",
            "gapa": "1",
            "provname": "Koshi",
            "dname": "District A",
            "gapaname": "Municipality A",
            "nHhld": "120",
            "total": "600",
            "male": "310",
            "female": "290",
        })

    monkeypatch.setattr(
        population_transform, "RAW_FILE", sample_file
    )

    import pytest

    with pytest.raises(
        ValueError, match="Invalid geographic codes at CSV line 2"
    ):
        load_local_governments()


def test_load_local_governments_rejects_invalid_numeric_values(
    tmp_path, monkeypatch
):
    columns = [
        "prov", "dist", "gapa",
        "provname", "dname", "gapaname",
        "nHhld", "total", "male", "female",
    ]

    sample_file = tmp_path / "invalid_numeric_values.csv"

    with sample_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerow({
            "prov": "1",
            "dist": "1",
            "gapa": "1",
            "provname": "Koshi",
            "dname": "District A",
            "gapaname": "Municipality A",
            "nHhld": "120",
            "total": "six hundred",
            "male": "310",
            "female": "290",
        })

    monkeypatch.setattr(
        population_transform, "RAW_FILE", sample_file
    )

    import pytest

    with pytest.raises(
        ValueError, match="Invalid numeric value at CSV line 2"
    ):
        load_local_governments()


def test_validate_output_accepts_valid_records():
    records = []

    for code in range(1, 754):
        records.append({
            "province_code": 1,
            "district_code": code,
            "local_government_code": 1,
            "households": 120,
            "population_total": 600,
            "population_male": 310,
            "population_female": 290,
        })

    validate_output(records)
import pytest


def make_valid_records():
    records = []

    for code in range(1, 754):
        records.append({
            "province_code": 1,
            "district_code": code,
            "local_government_code": 1,
            "households": 120,
            "population_total": 600,
            "population_male": 310,
            "population_female": 290,
        })

    return records


def test_validate_output_rejects_duplicate_keys():
    records = make_valid_records()
    records[1]["province_code"] = records[0]["province_code"]
    records[1]["district_code"] = records[0]["district_code"]
    records[1]["local_government_code"] = records[0]["local_government_code"]

    with pytest.raises(ValueError, match="Duplicate geographic key"):
        validate_output(records)


def test_validate_output_rejects_invalid_local_government_code():
    records = make_valid_records()
    records[0]["local_government_code"] = 99

    with pytest.raises(ValueError, match="Invalid local-government code"):
        validate_output(records)


def test_validate_output_rejects_negative_population():
    records = make_valid_records()
    records[0]["population_male"] = -10
    records[0]["population_female"] = 610

    with pytest.raises(ValueError, match="Negative population_male"):
        validate_output(records)


def test_validate_output_rejects_population_mismatch():
    records = make_valid_records()
    records[0]["population_total"] = 601

    with pytest.raises(ValueError, match="Population mismatch"):
        validate_output(records)

def test_transform_does_not_write_output_when_validation_fails(
    monkeypatch, tmp_path
):
    output_file = tmp_path / "local_government_population.csv"

    monkeypatch.setattr(
        population_transform,
        "load_local_governments",
        lambda: [],
    )
    monkeypatch.setattr(
        population_transform,
        "OUTPUT_FILE",
        output_file,
    )

    with pytest.raises(ValueError):
        population_transform.transform_population()

    assert not output_file.exists()
