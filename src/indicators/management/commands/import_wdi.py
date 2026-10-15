
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from indicators.models import Indicator, IndicatorObservation


EXPECTED_COLUMNS = [
    "country_name",
    "country_code",
    "indicator_name",
    "indicator_code",
    "year",
    "value",
]

MAX_DIGITS = 43
DECIMAL_PLACES = 29
BATCH_SIZE = 2000


class Command(BaseCommand):
    help = "Import validated World Development Indicators data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/processed/wdi_nepal/indicators.csv",
            help="Path to the processed WDI CSV file.",
        )
        parser.add_argument(
            "--expected-rows",
            type=int,
            default=98868,
            help="Expected number of observations.",
        )

    def handle(self, *args, **options):
        input_path = Path(options["file"])

        if not input_path.is_file():
            raise CommandError(
                f"Input file does not exist: {input_path}"
            )

        try:
            indicators, observations = self.validate_file(
                input_path,
                options["expected_rows"],
            )
        except (ValueError, OSError, csv.Error) as exc:
            raise CommandError(str(exc)) from exc

        # No database writes have happened before this point.
        with transaction.atomic():
            Indicator.objects.bulk_create(
                [
                    Indicator(
                        code=code,
                        name=name,
                        source="World Development Indicators",
                    )
                    for code, name in indicators.items()
                ],
                batch_size=BATCH_SIZE,
                update_conflicts=True,
                update_fields=["name", "source"],
                unique_fields=["code"],
            )

            indicator_ids = dict(
                Indicator.objects.filter(
                    code__in=indicators.keys()
                ).values_list("code", "id")
            )

            if len(indicator_ids) != len(indicators):
                raise CommandError(
                    "Could not resolve every indicator after upsert."
                )

            observation_objects = [
                IndicatorObservation(
                    indicator_id=indicator_ids[indicator_code],
                    country_code=country_code,
                    year=year,
                    value=value,
                )
                for (
                    country_code,
                    indicator_code,
                    year,
                    value,
                ) in observations
            ]

            IndicatorObservation.objects.bulk_create(
                observation_objects,
                batch_size=BATCH_SIZE,
                update_conflicts=True,
                update_fields=["value"],
                unique_fields=[
                    "indicator",
                    "country_code",
                    "year",
                ],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(observations)} observations "
                f"across {len(indicators)} indicators."
            )
        )

    def validate_file(self, input_path, expected_rows):
        indicators = {}
        observations = []
        seen_keys = set()
        country_names = {}
        row_count = 0

        with input_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames != EXPECTED_COLUMNS:
                raise ValueError(
                    "Unexpected CSV headers. Expected exactly: "
                    + ", ".join(EXPECTED_COLUMNS)
                )

            for row_number, row in enumerate(reader, start=2):
                row_count += 1

                if None in row:
                    raise ValueError(
                        f"Unexpected extra columns at row {row_number}."
                    )

                if any(
                    row.get(column) is None
                    for column in EXPECTED_COLUMNS
                ):
                    raise ValueError(
                        f"Missing column value at row {row_number}."
                    )

                country_name = row["country_name"].strip()
                country_code = row["country_code"].strip()
                indicator_name = row["indicator_name"].strip()
                indicator_code = row["indicator_code"].strip()
                year_text = row["year"].strip()
                raw_value = row["value"].strip()

                if not all(
                    [
                        country_name,
                        country_code,
                        indicator_name,
                        indicator_code,
                        year_text,
                    ]
                ):
                    raise ValueError(
                        f"Missing identifier at row {row_number}."
                    )

                if (
                    len(country_code) != 3
                    or not country_code.isascii()
                    or not country_code.isalpha()
                    or country_code != country_code.upper()
                ):
                    raise ValueError(
                        f"Invalid country code {country_code!r} "
                        f"at row {row_number}."
                    )

                try:
                    year = int(year_text)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid year {year_text!r} "
                        f"at row {row_number}."
                    ) from exc

                if not 1960 <= year <= 2100:
                    raise ValueError(
                        f"Year {year} is outside the allowed range "
                        f"at row {row_number}."
                    )

                previous_country_name = country_names.get(country_code)

                if (
                    previous_country_name is not None
                    and previous_country_name != country_name
                ):
                    raise ValueError(
                        f"Inconsistent country names for "
                        f"{country_code!r} at row {row_number}."
                    )

                country_names[country_code] = country_name

                previous_indicator_name = indicators.get(indicator_code)

                if (
                    previous_indicator_name is not None
                    and previous_indicator_name != indicator_name
                ):
                    raise ValueError(
                        f"Inconsistent names for indicator "
                        f"{indicator_code!r} at row {row_number}."
                    )

                indicators[indicator_code] = indicator_name

                key = (country_code, indicator_code, year)

                if key in seen_keys:
                    raise ValueError(
                        f"Duplicate observation {key!r} "
                        f"at row {row_number}."
                    )

                seen_keys.add(key)

                value = None

                if raw_value:
                    try:
                        value = Decimal(raw_value)
                    except InvalidOperation as exc:
                        raise ValueError(
                            f"Invalid decimal {raw_value!r} "
                            f"at row {row_number}."
                        ) from exc

                    if not value.is_finite():
                        raise ValueError(
                            f"Non-finite decimal {raw_value!r} "
                            f"at row {row_number}."
                        )

                    decimal_tuple = value.as_tuple()
                    exponent = decimal_tuple.exponent
                    digits = len(decimal_tuple.digits)

                    actual_decimal_places = max(-exponent, 0)
                    actual_integer_digits = max(
                        digits + exponent, 0
                    )

                    if actual_decimal_places > DECIMAL_PLACES:
                        raise ValueError(
                            f"Too many decimal places in {raw_value!r} "
                            f"at row {row_number}; maximum is "
                            f"{DECIMAL_PLACES}."
                        )

                    if actual_integer_digits > (
                        MAX_DIGITS - DECIMAL_PLACES
                    ):
                        raise ValueError(
                            f"Too many integer digits in {raw_value!r} "
                            f"at row {row_number}; maximum is "
                            f"{MAX_DIGITS - DECIMAL_PLACES}."
                        )

                observations.append(
                    (
                        country_code,
                        indicator_code,
                        year,
                        value,
                    )
                )

        if row_count != expected_rows:
            raise ValueError(
                f"Expected {expected_rows} observations, "
                f"found {row_count}."
            )

        return indicators, observations
