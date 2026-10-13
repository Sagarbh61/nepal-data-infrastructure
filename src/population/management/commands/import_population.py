import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from population.models import LocalGovernmentPopulation

EXPECTED_COLUMNS = [
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

NUMERIC_FIELDS = [
  "province_code",
  "district_code",
  "local_government_code",
  "households",
  "population_total",
  "population_male",
  "population_female"
]

UPDATE_FIELDS = [
  "province_name",
  "district_name",
  "local_government_name",
  "households",
  "population_total",
  "population_male",
  "population_female"
]

class Command(BaseCommand):
  help = "Import validated local-government population data."

  def add_arguments(self, parser):
    parser.add_argument(
      "--csv",
      type=Path,
      default=(
        settings.BASE_DIR.parent
        / "data"
        / "processed"
        / "nphc_2021"
        / "local_government_population.csv"
      ),
      help = "Path to the processed population CSV."
    ),
    parser.add_argument(
      "--expected_rows",
      type=int,
      default=753,
      help="Expected number of records (default: 753).",
    )

  def handle(self, *args, **options):
    csv_path = options["csv"]
    expected_rows = options["expected_rows"]

    if not csv_path.is_file():
      raise CommandError(f"CSV file is not found: {csv_path}")

    if expected_rows < 1:
      raise CommandError("--expected rows must be at least 1.")

    records = []
    seen_keys = set()

    # validate the complete csv before writing anything

    try:
      with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
      ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != EXPECTED_COLUMNS:
          raise CommandError(
            "CSV headers do not match the expected schema.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Found:    {reader.fieldnames}"
          )

        for line_number, row in enumerate(reader, start=2):
          if None in row or any(
            value is None or not value.strip()
            for value in row.values()
          ):
            raise CommandError(
              f"Line {line_number}: missing or extra CSV data."
            )
          try:
            for field in NUMERIC_FIELDS:
              row[field] = int(row[field])
          except ValueError as exc:
            raise CommandError(
              f"Line {line_number}: invalid integer value."
            ) from exc

          if (row["province_code"] < 1 or row["district_code"] < 1):
            raise CommandError(
            f"Line number {line_number}: province and district "
            "Codes must be positive."
            )

          code = row["local_government_code"]

          if not 1 <= code <= 98:
            raise CommandError(
              f"Line {line_number}: local government code"
              f"{code}is outside the range 1-98"
            )

          if (row["population_total"] != row["population_male"] + row["population_female"]):
            raise CommandError(
              f"Line {line_number}: male and female population "
              "do not sum to the total"
            )
          if any ( row[field] < 1 for field in NUMERIC_FIELDS[:3]):
            raise CommandError(f"Line {line_number}: counts cannot be negative.")

          for field in (
            "province_name",
            "district_name",
            "local_government_name"
          ):
            row[field] = row[field].strip()

          key = (
            2021,
            row["province_code"],
            row["district_code"],
            row["local_government_code"],
          )

          if key in seen_keys:
            raise CommandError(
              f"Line {line_number}: duplicate geographic key "
              f"{key}."
            )

          seen_keys.add(key)
          records.append(
            LocalGovernmentPopulation(
              **row,
              census_year=2021,
            )
          )
    except UnicodeDecodeError as exc:
      raise CommandError("Could not decode the CSV as UTF-8.") from exc

    if len(records) != expected_rows:
      raise CommandError(
        f"Expected {expected_rows} records, "
        f"but found {len(records)}. Nothing was imported."
      )

    # Import atomicall; reruns update matching geographic records.

    with transaction.atomic():
      LocalGovernmentPopulation.objects.bulk_create(
        records,
        batch_size=500,
        update_conflicts=True,
        update_fields=UPDATE_FIELDS,
        unique_fields=[
          "census_year",
          "province_code",
          "district_code",
          "local_government_code"
        ],
      )

    self.stdout.write(
      self.style.SUCCESS(
        f"Successfully imported or updated {len(records)} "
        f"records for the 2021 census from {csv_path}."
      )
    )
