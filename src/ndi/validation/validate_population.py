
import csv
from collections import Counter, defaultdict
from pathlib import Path


# --------------------------------------------------
# 1. FILE CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "nphc_2021"
    / "Indv01_PopulationBySex.csv"
)

REQUIRED_COLUMNS = [
    "prov", "dist", "gapa",
    "provname", "dname", "gapaname",
    "nHhld", "total", "male", "female",
]

NUMERIC_FIELDS = ["nHhld", "total", "male", "female"]


# --------------------------------------------------
# 2. CLASSIFY RECORDS
# --------------------------------------------------

def classify_row(prov, dist, gapa):
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

    return None


# --------------------------------------------------
# 3. LOAD AND PARSE THE SOURCE
# --------------------------------------------------

def load_records():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {RAW_FILE}")

    with RAW_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        columns = reader.fieldnames or []
        missing_columns = [
            column for column in REQUIRED_COLUMNS
            if column not in columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        records = []

        for line_number, raw in enumerate(reader, start=2):
            record = {
                "line": line_number,
                "raw": raw,
                "codes": None,
                "type": None,
            }

            # Parse geographic codes.
            try:
                prov = int(raw["prov"])
                dist = int(raw["dist"])
                gapa = int(raw["gapa"])

                record["codes"] = (prov, dist, gapa)
                record["type"] = classify_row(prov, dist, gapa)

            except (ValueError, TypeError):
                pass

            # Parse numeric measures.
            record["values"] = {}

            for field in NUMERIC_FIELDS:
                try:
                    record["values"][field] = int(raw[field])
                except (ValueError, TypeError):
                    record["values"][field] = None

            records.append(record)

    return records


# --------------------------------------------------
# 4. VALIDATION HELPERS
# --------------------------------------------------

def validate_population_arithmetic(records, issues):
    for record in records:
        values = record["values"]

        for field in NUMERIC_FIELDS:
            value = values[field]

            if value is None:
                issues.append(
                    f"Line {record['line']}: "
                    f"missing or invalid numeric value in {field}"
                )
            elif value < 0:
                issues.append(
                    f"Line {record['line']}: "
                    f"negative value in {field}: {value}"
                )

        total = values["total"]
        male = values["male"]
        female = values["female"]

        if all(v is not None for v in [total, male, female]):
            if male + female != total:
                issues.append(
                    f"Line {record['line']}: "
                    f"male + female != total"
                )


def validate_keys_and_hierarchy(records, issues):
    key_counts = Counter(
        record["codes"]
        for record in records
        if record["codes"] is not None
    )

    for key, count in key_counts.items():
        if count > 1:
            issues.append(
                f"Duplicate geographic key {key}: {count} records"
            )

    # Index the aggregate records by their source codes.
    provinces = {}
    districts = {}

    for record in records:
        codes = record["codes"]

        if codes is None:
            issues.append(
                f"Line {record['line']}: invalid geographic codes"
            )
            continue

        prov, dist, gapa = codes

        if record["type"] == "province":
            provinces[prov] = record

        elif record["type"] == "district":
            districts[(prov, dist)] = record

    for record in records:
        if record["type"] not in {
            "district", "local_government", "institutional"
        }:
            continue

        prov, dist, _ = record["codes"]

        if prov not in provinces:
            issues.append(
                f"Line {record['line']}: "
                f"province aggregate missing for code {prov}"
            )

        if record["type"] in {"local_government", "institutional"}:
            if (prov, dist) not in districts:
                issues.append(
                    f"Line {record['line']}: "
                    f"district aggregate missing for codes {(prov, dist)}"
                )


def reconcile_aggregates(parent, children, description, issues):
    if not children:
        issues.append(f"{description}: no child records found")
        return

    for field in NUMERIC_FIELDS:
        parent_value = parent["values"][field]
        child_values = [
            child["values"][field] for child in children
        ]

        # Don't report misleading sums when inputs are invalid.
        if parent_value is None or any(
            value is None for value in child_values
        ):
            continue

        child_total = sum(child_values)

        if parent_value != child_total:
            issues.append(
                f"{description}: {field} mismatch; "
                f"aggregate={parent_value}, children={child_total}"
            )


# --------------------------------------------------
# 5. VALIDATE AGGREGATE TOTALS
# --------------------------------------------------

def validate_reconciliation(records, issues):
    national_rows = []
    province_rows = {}
    district_rows = {}

    district_children = defaultdict(list)
    province_children = defaultdict(list)
    national_children = []

    for record in records:
        row_type = record["type"]
        codes = record["codes"]

        if row_type == "national":
            national_rows.append(record)

        elif row_type == "province":
            province_rows[codes[0]] = record
            national_children.append(record)

        elif row_type == "district":
            prov, dist, _ = codes
            district_rows[(prov, dist)] = record
            province_children[prov].append(record)

        elif row_type in {"local_government", "institutional"}:
            prov, dist, _ = codes
            district_children[(prov, dist)].append(record)

    if len(national_rows) != 1:
        issues.append(
            f"Expected 1 national aggregate, found {len(national_rows)}"
        )

    # Each district = local governments + institutional record.
    for key, district in district_rows.items():
        reconcile_aggregates(
            district,
            district_children[key],
            f"District {key}",
            issues,
        )

    # Each province = sum of its district aggregates.
    for prov, province in province_rows.items():
        reconcile_aggregates(
            province,
            province_children[prov],
            f"Province {prov}",
            issues,
        )

    # National total = sum of province aggregates.
    if len(national_rows) == 1:
        reconcile_aggregates(
            national_rows[0],
            national_children,
            "National total",
            issues,
        )


# --------------------------------------------------
# 6. RUN VALIDATION AND PRINT RESULTS
# --------------------------------------------------

def validate_population():
    records = load_records()
    issues = []

    row_types = Counter(
        record["type"] or "unclassified"
        for record in records
    )

    validate_population_arithmetic(records, issues)
    validate_keys_and_hierarchy(records, issues)
    validate_reconciliation(records, issues)

    print("\n" + "=" * 55)
    print("NEPAL DATA INFRASTRUCTURE")
    print("Population Data Validation Report")
    print("=" * 55)

    print(f"\nSource file: {RAW_FILE.name}")
    print(f"Total records: {len(records)}")

    print("\n--- Record Counts ---")
    for row_type, count in sorted(row_types.items()):
        print(f"{row_type:<22} {count:>5}")

    print("\n--- Validation Result ---")

    if issues:
        print(f"FAILED: {len(issues)} issue(s) found.")

        for issue in issues:
            print(f"  - {issue}")
    else:
        print("PASSED: All implemented validation rules passed.")

    print("\nRaw source file was not modified.")
    print("=" * 55)


if __name__ == "__main__":
    validate_population()