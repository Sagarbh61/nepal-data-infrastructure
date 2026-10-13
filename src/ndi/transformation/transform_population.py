
import csv
from pathlib import Path


# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nphc_2021"
    / "Indv01_PopulationBySex.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "nphc_2021"
)

OUTPUT_FILE = OUTPUT_DIR / "local_government_population.csv"


# --------------------------------------------------
# 2. TRANSFORMATION RULES
# --------------------------------------------------

COLUMN_MAPPING = {
    "prov": "province_code",
    "dist": "district_code",
    "gapa": "local_government_code",
    "provname": "province_name",
    "dname": "district_name",
    "gapaname": "local_government_name",
    "nHhld": "households",
    "total": "population_total",
    "male": "population_male",
    "female": "population_female",
}

OUTPUT_COLUMNS = list(COLUMN_MAPPING.values())


def classify_row(row):
    prov = int(row["prov"])
    dist = int(row["dist"])
    gapa = int(row["gapa"])

    if prov == 0 and dist == 0 and gapa == 0:
        return "national"

    if prov > 0 and dist == 0 and gapa == 0:
        return "province"

    if prov > 0 and dist > 0 and gapa == 0:
        return "district"

    if prov > 0 and dist > 0 and 1 <= gapa <= 98:
        return "local_government"

    if prov > 0 and dist > 0 and gapa == 99:
        return "institutional"

    return "unclassified"


# --------------------------------------------------
# 3. READ AND SELECT RECORDS
# --------------------------------------------------

def load_local_governments():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {RAW_FILE}"
        )

    with RAW_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("The source CSV has no header.")

        missing_columns = [
            column
            for column in COLUMN_MAPPING
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        selected_records = []

        for line_number, row in enumerate(reader, start=2):
            try:
                row_type = classify_row(row)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid geographic codes at CSV line "
                    f"{line_number}"
                )

            if row_type != "local_government":
                continue

            transformed = {}

            for source_column, output_column in COLUMN_MAPPING.items():
                value = row[source_column].strip()

                if not value:
                    raise ValueError(
                        f"Missing {source_column} at CSV line "
                        f"{line_number}"
                    )

                transformed[output_column] = value

            # Convert numeric fields to integers.
            numeric_columns = [
                "province_code",
                "district_code",
                "local_government_code",
                "households",
                "population_total",
                "population_male",
                "population_female",
            ]

            try:
                for column in numeric_columns:
                    transformed[column] = int(transformed[column])
            except ValueError as error:
                raise ValueError(
                    f"Invalid numeric value at CSV line "
                    f"{line_number}: {error}"
                ) from error

            selected_records.append(transformed)

    return selected_records


# --------------------------------------------------
# 4. CHECK THE TRANSFORMED DATA
# --------------------------------------------------

def validate_output(records):
    issues = []

    if len(records) != 753:
        issues.append(
            f"Expected 753 local governments, found {len(records)}"
        )

    seen_keys = set()

    for record in records:
        key = (
            record["province_code"],
            record["district_code"],
            record["local_government_code"],
        )

        if key in seen_keys:
            issues.append(f"Duplicate geographic key: {key}")

        seen_keys.add(key)

        if record["local_government_code"] not in range(1, 99):
            issues.append(
                f"Invalid local-government code: {key}"
            )

        for field in [
            "households",
            "population_total",
            "population_male",
            "population_female",
        ]:
            if record[field] < 0:
                issues.append(
                    f"Negative {field} for geographic key {key}"
                )

        if (
            record["population_male"]
            + record["population_female"]
            != record["population_total"]
        ):
            issues.append(
                f"Population mismatch for geographic key {key}"
            )

    if issues:
        preview = "\n".join(f"- {issue}" for issue in issues[:20])

        raise ValueError(
            f"Transformation validation failed with "
            f"{len(issues)} issue(s):\n{preview}"
        )


# --------------------------------------------------
# 5. WRITE THE PROCESSED DATASET
# --------------------------------------------------

def transform_population():
    records = load_local_governments()

    # Do not write an output until the checks pass.
    validate_output(records)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(records)

    print("\n" + "=" * 55)
    print("NEPAL DATA INFRASTRUCTURE")
    print("Population Transformation Report")
    print("=" * 55)

    print(f"\nSource: {RAW_FILE.name}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Records written: {len(records)}")
    print(f"Columns written: {len(OUTPUT_COLUMNS)}")
    print("Duplicate geographic keys: 0")
    print("Population mismatches: 0")
    print("Output validation: PASSED")
    print("Raw source modified: No")

    print("\nTransformation complete.")
    print("=" * 55)


if __name__ == "__main__":
    transform_population()