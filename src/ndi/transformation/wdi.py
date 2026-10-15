import argparse
import csv
from decimal import Decimal, InvalidOperation
import os
import tempfile
from pathlib import Path


IDENTIFIER_COLUMNS = [
    "Country Name",
    "Country Code",
    "Indicator Name",
    "Indicator Code",
]

EXPECTED_METADATA = {
    "Data Source": "World Development Indicators",
}


def transform_wdi_csv(input_path: Path, output_path: Path) -> int:
    with input_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        rows = list(csv.reader(file))

    if len(rows) < 5:
        raise ValueError(
            "WDI file is missing its header or metadata rows."
        )

    if rows[0][:2] != [
        "Data Source",
        EXPECTED_METADATA["Data Source"],
    ]:
        raise ValueError("Unexpected WDI data source metadata.")

    headers = rows[4]

    if headers[:4] != IDENTIFIER_COLUMNS:
        raise ValueError("Unexpected WDI column headers.")

    year_columns = (
        headers[4:-1] if headers[-1] == "" else headers[4:]
    )

    try:
        years = [int(year) for year in year_columns]
    except ValueError as exc:
        raise ValueError(
            "WDI header contains an invalid year column."
        ) from exc

    if len(years) != len(set(years)):
        raise ValueError("Duplicate year columns found.")

    output_columns = [
        "country_name",
        "country_code",
        "indicator_name",
        "indicator_code",
        "year",
        "value",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_count = 0

    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    )

    try:
        with os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=output_columns,
            )
            writer.writeheader()

            for row_number, row in enumerate(rows[5:], start=6):
                if not row or all(not value for value in row):
                    continue

                if len(row) != len(headers):
                    raise ValueError(
                        f"Row {row_number} has {len(row)} columns: "
                        f"expected {len(headers)}"
                    )

                if headers[-1] == "" and row[-1] != "":
                    raise ValueError(
                        f"Row {row_number} has a value in the "
                        "empty trailing column."
                    )

                (
                    country_name,
                    country_code,
                    indicator_name,
                    indicator_code,
                ) = row[:4]

                if not all(
                    [
                        country_name,
                        country_code,
                        indicator_name,
                        indicator_code,
                    ]
                ):
                    raise ValueError(
                        f"Missing identifier at row {row_number}."
                    )

                for year, raw_value in zip(
                    years,
                    row[4:4 + len(years)],
                ):
                    # Preserve source text while validating numeric values.
                    value = raw_value.strip()

                    if value:
                        try:
                            numeric_value = Decimal(value)
                        except InvalidOperation as exc:
                            raise ValueError(
                                f"Non-numeric value {value!r} "
                                f"at row {row_number}, year {year}."
                            ) from exc

                        if not numeric_value.is_finite():
                            raise ValueError(
                                f"Non-finite value {value!r} "
                                f"at row {row_number}, year {year}."
                            )

                    writer.writerow(
                        {
                            "country_name": country_name,
                            "country_code": country_code,
                            "indicator_name": indicator_name,
                            "indicator_code": indicator_code,
                            "year": year,
                            "value": value,
                        }
                    )
                    output_count += 1

        # Publish the output only after successful processing.
        Path(temporary_name).replace(output_path)

    except BaseException:
        # Clean up temporary resources and preserve the original exception.
        try:
            os.close(file_descriptor)
        except OSError:
            pass

        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass

        raise

    return output_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transform World Development Indicators CSV data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(
            "data/raw/wdi_nepal/API_NPL_DS2_en_csv_v2_18651.csv"
        ),
        help="Path to the raw WDI CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/wdi_nepal/indicators.csv"),
        help="Path for the transformed CSV file.",
    )

    args = parser.parse_args()

    try:
        count = transform_wdi_csv(args.input, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Transformation failed: {exc}\n")

    print(f"Transformed {count} observations.")
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
