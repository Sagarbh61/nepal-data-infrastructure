import csv

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


from population.models import LocalGovernmentPopulation

@pytest.mark.django_db

def test_import_population_creates_record(tmp_path):
  csv_path = tmp_path / "population.csv"
  headers = [
        "province_code",
        "district_code",
        "local_government_code",
        "province_name",
        "district_name",
        "local_government_name",
        "households",
        "population_total",
        "population_male",
        "population_female",
    ]
  row = {
        "province_code": 1,
        "district_code": 1,
        "local_government_code": 1,
        "province_name": "Province-1",
        "district_name": "Taplejung",
        "local_government_name": "Phaktanlung Gaunpalika",
        "households": 2832,
        "population_total": 11791,
        "population_male": 6088,
        "population_female": 5703,
    }

  with csv_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames= headers)
    writer.writeheader()
    writer.writerow(row)

  call_command(
    "import_population",
    csv=csv_path,
    expected_rows = 1,
  )

  assert LocalGovernmentPopulation.objects.count() == 1

  record = LocalGovernmentPopulation.objects.get()

  assert record.local_government_name == "Phaktanlung Gaunpalika"
  assert record.population_total ==  11791
  assert record.census_year == 2021



@pytest.mark.django_db
def test_import_population_rejects_duplicate_geographic_key(tmp_path):
  csv_path = tmp_path / "population.csv"
  headers = [
        "province_code",
        "district_code",
        "local_government_code",
        "province_name",
        "district_name",
        "local_government_name",
        "households",
        "population_total",
        "population_male",
        "population_female",
    ]

  row = {
        "province_code": 1,
        "district_code": 1,
        "local_government_code": 1,
        "province_name": "Province-1",
        "district_name": "Taplejung",
        "local_government_name": "Phaktanlung Gaunpalika",
        "households": 2832,
        "population_total": 11791,
        "population_male": 6088,
        "population_female": 5703,
    }
  with csv_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerow(row)
    writer.writerow(row)

  with pytest.raises(CommandError, match="duplicate geographic key"):
    call_command(
      "import_population",
      csv=csv_path,
      expected_rows = 2,
    )

  assert LocalGovernmentPopulation.objects.count() == 0

@pytest.mark.django_db
def test_import_population_rejects_invalid_population_total(tmp_path):
  csv_path = tmp_path / "population.csv"
  headers = [
        "province_code",
        "district_code",
        "local_government_code",
        "province_name",
        "district_name",
        "local_government_name",
        "households",
        "population_total",
        "population_male",
        "population_female",
    ]

  row = {
        "province_code": 1,
        "district_code": 1,
        "local_government_code": 1,
        "province_name": "Province-1",
        "district_name": "Taplejung",
        "local_government_name": "Phaktanlung Gaunpalika",
        "households": 2832,
        "population_total": 12000,
        "population_male": 6088,
        "population_female": 5703,
    }

  with csv_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerow(row)

  with pytest.raises(CommandError, match="population"):
    call_command(
      "import_population",
      csv=csv_path,
      expected_rows=1
    )
  assert LocalGovernmentPopulation.objects.count() == 0


@pytest.mark.django_db
def test_import_population_can_run_twice_without_duplicates(tmp_path):
    csv_path = tmp_path / "population.csv"

    headers = [
        "province_code",
        "district_code",
        "local_government_code",
        "province_name",
        "district_name",
        "local_government_name",
        "households",
        "population_total",
        "population_male",
        "population_female",
    ]

    row = {
        "province_code": 1,
        "district_code": 1,
        "local_government_code": 1,
        "province_name": "Province-1",
        "district_name": "Taplejung",
        "local_government_name": "Phaktanlung Gaunpalika",
        "households": 2832,
        "population_total": 11791,
        "population_male": 6088,
        "population_female": 5703,
    }

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(row)

    call_command(
        "import_population",
        csv=csv_path,
        expected_rows=1,
    )

    assert LocalGovernmentPopulation.objects.count() == 1

    call_command(
        "import_population",
        csv=csv_path,
        expected_rows=1,
    )

    assert LocalGovernmentPopulation.objects.count() == 1


@pytest.mark.django_db
def test_import_population_rejects_file_without_partial_import(tmp_path):
    csv_path = tmp_path / "population.csv"

    headers = [
        "province_code",
        "district_code",
        "local_government_code",
        "province_name",
        "district_name",
        "local_government_name",
        "households",
        "population_total",
        "population_male",
        "population_female",
    ]

    valid_row = {
        "province_code": 1,
        "district_code": 1,
        "local_government_code": 1,
        "province_name": "Province-1",
        "district_name": "Taplejung",
        "local_government_name": "Phaktanlung Gaunpalika",
        "households": 2832,
        "population_total": 11791,
        "population_male": 6088,
        "population_female": 5703,
    }

    invalid_row = {
        **valid_row,
        "district_code": 2,
        "local_government_code": 2,
        "district_name": "Invalid District",
        "local_government_name": "Invalid Municipality",
        "population_total": 12000,
    }

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(valid_row)
        writer.writerow(invalid_row)

    with pytest.raises(CommandError, match="population"):
        call_command(
            "import_population",
            csv=csv_path,
            expected_rows=2,
        )

    assert LocalGovernmentPopulation.objects.count() == 0


@pytest.mark.django_db
def test_import_population_rejects_wrong_headers(tmp_path):
    csv_path = tmp_path / "population.csv"

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "province_code",
            "district_code",
            "wrong_column_name",
        ])

    with pytest.raises(CommandError, match="CSV headers"):
        call_command(
            "import_population",
            csv=csv_path,
            expected_rows=1,
        )

    assert LocalGovernmentPopulation.objects.count() == 0