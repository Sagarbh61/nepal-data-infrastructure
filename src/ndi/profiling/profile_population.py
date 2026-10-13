import csv
from collections import Counter
from pathlib import Path

# File Paths

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_FILE = (PROJECT_ROOT / "data" / "raw" / "nphc_2021" / "Indv01_PopulationBySex.csv")


# Expected Structure
REQUIRED_COLUMNS = [
  "prov",
  "dist",
  "gapa",
  "provname",
  "dname",
  "gapaname",
  "nHhld",
  "total",
  "male",
  "female",
]

# Classify Geographics Rows

def classify_row(row):
  prov = int(row["prov"])
  dist = int(row['dist'])
  gapa = int(row["gapa"])

  if prov == 0 and dist == 0 and gapa == 0:
    return "national total"

  if prov > 0 and dist == 0 and gapa == 0:
    return "province total"

  if prov > 0 and dist > 0 and gapa == 0:
    return "district total"

  if prov > 0 and dist > 0 and 1<= gapa <=98:
    return "local government"

  if prov > 0 and dist > 0 and gapa == 99:
    return "INSTITUTIONAL"

  return "unclassified"

# Profiling raw csv

def profile_population():
  if not RAW_FILE.exists():
    raise FileNotFoundError("" \
    f"CSV not found: {RAW_FILE}\n"
    "Check that the file is in data/raw/nhpc_2021/."
    )

  with RAW_FILE.open("r", encoding = "utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    columns = reader.fieldnames or []
    missing_columns = [
      column
      for column in REQUIRED_COLUMNS
      if column not in columns
    ]

    if missing_columns:
      raise ValueError('' \
      f'Missing required columns: {missing_columns}')

    rows = list(reader)

  row_types = Counter()
  duplicate_keys = Counter()
  missing_values = Counter()
  population_mismatches = []
  unclassified_rows = []

  for line_number, row in enumerate(rows, start=2):
    # count row types
    try:
      row_type = classify_row(row)
    except (ValueError, TypeError):
      row_type = "unclassified"

    row_types[row_type] += 1

    if row_type == "unclassified":
      unclassified_rows.append(line_number)

    # check uniqueness of source geographic codes
    key = (row["prov"], row["dist"], row["gapa"])
    duplicate_keys[key] += 1

    # check missing values in core fields
    for column in REQUIRED_COLUMNS:
      if not (row.get(column) or "").strip():
        missing_values[column] += 1

    # Check population arithmetic where values are present
    try:
      total = int(row['total'])
      male = int(row["male"])
      female = int(row["female"])

      if male + female != total:
        population_mismatches.append(
          {
            "line":line_number,
            "name":row["gapaname"],
            "total":total,
            "male_plus_female":male + female,
          }
        )
    except (ValueError, TypeError):
      pass

  duplicate_keys = {
    key:count
    for key, count in duplicate_keys.items()
    if count > 1
  }

# print the report
  print("\n" + "=" * 55)
  print("NEPAL DATA INFRASTRUCTURE")
  print("=" * 55)

  print(f"\nSource file:{RAW_FILE.name}")
  print(f"Columns: {len(columns)}")
  print(f"Rows: {len(rows)}")

  print("\n--- Row Classification ---")
  for row_type, count in sorted(row_types.items()):
    print(f"{row_type:<22} {count:>5}")

  print("\n--- Data Quality Chekcs ---")
  print(f"Duplicate Geographic keys: {len(duplicate_keys)}")
  print(f"Rows with population mismatch: {len(population_mismatches)}")
  print(f"Unclassified rows: {len(unclassified_rows)}")

  print("\nMissing values in core columns")
  for column in REQUIRED_COLUMNS:
    print(f"{column:<15} {missing_values[column]:>5}")

  if duplicate_keys:
    print("\nDuplicate Keys (first 10)")

    for key, count in list(duplicate_keys.items())[:10]:
      print(f"{key} appears {count} times in ")

  if population_mismatches:
    print("\nPopulation mismatches (first 10)")
    for item in population_mismatches[:10]:
      print(
        f" Line {item['line']} : {item['name']}"
        f"total = {item['total']}"
        f"male + female={item['male_plus_female']}"

      )
  if unclassified_rows:
    print("\nUnclassified CSV lines (first 10): ")
    print(f" {unclassified_rows[:10]}")


  print("\n" + "=" * 55)
  print("Profiling complete. Raw data was not modified.")
  print("=" * 55)

if __name__ == "__main__":
  profile_population()
