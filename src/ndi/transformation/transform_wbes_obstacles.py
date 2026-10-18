import csv
from pathlib import Path

import pyreadstat

from ndi.transformation.wbes_obstacles import (
    calculate_obstacle_share,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "wbes_2023"
    / "Nepal-2023-full-data.dta"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "wbes_2023"
OUTPUT_FILE = OUTPUT_DIR / "business_obstacles.csv"

WEIGHT_COLUMN = "wmedian"

OBSTACLES = [
    "c30a", "d30a", "d30b", "e30", "g30a",
    "j30a", "j30b", "j30c", "j30e", "j30f",
    "h30", "i30", "k30", "l30a",
]

OUTPUT_COLUMNS = [
    "obstacle",
    "label",
    "weight",
    "total_records",
    "valid_responses",
    "excluded_responses",
    "major_or_severe_responses",
    "unweighted_share",
    "weighted_share",
]


def build_obstacle_summary(dataframe, variable_labels):
    results = []

    for column in OBSTACLES:
        result = calculate_obstacle_share(
            dataframe,
            obstacle_column=column,
            weight_column=WEIGHT_COLUMN,
        )

        result["label"] = variable_labels.get(column, column)
        results.append(result)

    return sorted(
        results,
        key=lambda result: result["weighted_share"],
        reverse=True,
    )


def validate_summary(results, source_record_count):
    issues = []

    if len(results) != len(OBSTACLES):
        issues.append(
            f"Expected {len(OBSTACLES)} indicators, found {len(results)}"
        )

    seen = set()

    for result in results:
        obstacle = result["obstacle"]

        if obstacle in seen:
            issues.append(f"Duplicate indicator: {obstacle}")
        seen.add(obstacle)

        if result["total_records"] != source_record_count:
            issues.append(
                f"{obstacle}: source record count mismatch"
            )

        if (
            result["valid_responses"] + result["excluded_responses"]
            != source_record_count
        ):
            issues.append(
                f"{obstacle}: response counts do not add up"
            )

        for field in ["weighted_share", "unweighted_share"]:
            value = result[field]

            if not 0 <= value <= 1:
                issues.append(
                    f"{obstacle}: {field} outside 0 to 1"
                )

    if issues:
        raise ValueError(
            "Summary validation failed:\n"
            + "\n".join(f"- {issue}" for issue in issues)
        )


def transform_wbes_obstacles():
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {RAW_FILE}"
        )

    dataframe, metadata = pyreadstat.read_dta(
        str(RAW_FILE),
        apply_value_formats=False,
    )

    variable_labels = dict(
        zip(metadata.column_names, metadata.column_labels or [])
    )

    results = build_obstacle_summary(dataframe, variable_labels)
    validate_summary(results, len(dataframe))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )
        writer.writeheader()

        for result in results:
            writer.writerow({
                column: result[column]
                for column in OUTPUT_COLUMNS
            })

    print("=" * 60)
    print("NEPAL DATA INFRASTRUCTURE")
    print("WBES 2023 Business Obstacle Transformation")
    print("=" * 60)
    print(f"Source: {RAW_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Source records: {len(dataframe)}")
    print(f"Indicators written: {len(results)}")
    print(f"Survey weight: {WEIGHT_COLUMN}")
    print("Summary validation: PASSED")
    print("Raw source modified: No")
    print("=" * 60)


if __name__ == "__main__":
    transform_wbes_obstacles()
