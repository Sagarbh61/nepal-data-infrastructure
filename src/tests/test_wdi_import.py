
import csv
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from indicators.models import Indicator, IndicatorObservation


HEADERS = [
    "country_name",
    "country_code",
    "indicator_name",
    "indicator_code",
    "year",
    "value",
]


def write_wdi_csv(tmp_path, rows, headers=HEADERS):
    csv_path = tmp_path / "wdi_test.csv"

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def sample_row(**overrides):
    row = {
        "country_name": "Nepal",
        "country_code": "NPL",
        "indicator_name": "GDP growth",
        "indicator_code": "NY.GDP.MKTP.KD.ZG",
        "year": "2020",
        "value": "2.345678901234567890123456789",
    }
    row.update(overrides)
    return row


@pytest.mark.django_db
def test_import_wdi_creates_indicator_and_observation(tmp_path):
    csv_path = write_wdi_csv(tmp_path, [sample_row()])

    call_command(
        "import_wdi",
        file=str(csv_path),
        expected_rows=1,
    )

    assert Indicator.objects.count() == 1
    assert IndicatorObservation.objects.count() == 1

    observation = IndicatorObservation.objects.get()

    assert observation.country_code == "NPL"
    assert observation.year == 2020
    assert observation.value == Decimal(
        "2.345678901234567890123456789"
    )
    assert observation.indicator.code == "NY.GDP.MKTP.KD.ZG"


@pytest.mark.django_db
def test_import_wdi_can_run_twice_without_duplicates(tmp_path):
    csv_path = write_wdi_csv(tmp_path, [sample_row()])

    call_command("import_wdi", file=str(csv_path), expected_rows=1)
    call_command("import_wdi", file=str(csv_path), expected_rows=1)

    assert Indicator.objects.count() == 1
    assert IndicatorObservation.objects.count() == 1


@pytest.mark.django_db
def test_import_wdi_rejects_invalid_value_without_partial_import(
    tmp_path,
):
    rows = [
        sample_row(),
        sample_row(
            indicator_code="TEST.INVALID",
            indicator_name="Invalid test indicator",
            year="2021",
            value="not-a-number",
        ),
    ]
    csv_path = write_wdi_csv(tmp_path, rows)

    with pytest.raises(CommandError, match="Invalid decimal"):
        call_command(
            "import_wdi",
            file=str(csv_path),
            expected_rows=2,
        )

    assert Indicator.objects.count() == 0
    assert IndicatorObservation.objects.count() == 0


@pytest.mark.django_db
def test_import_wdi_rejects_duplicate_observations(tmp_path):
    row = sample_row()
    csv_path = write_wdi_csv(tmp_path, [row, row])

    with pytest.raises(CommandError, match="Duplicate observation"):
        call_command(
            "import_wdi",
            file=str(csv_path),
            expected_rows=2,
        )

    assert Indicator.objects.count() == 0
    assert IndicatorObservation.objects.count() == 0


@pytest.mark.django_db
def test_import_wdi_rolls_back_when_observation_write_fails(tmp_path):
    csv_path = write_wdi_csv(tmp_path, [sample_row()])

    with patch(
        "indicators.management.commands.import_wdi."
        "IndicatorObservation.objects.bulk_create",
        side_effect=RuntimeError("Simulated database failure"),
    ):
        with pytest.raises(
            RuntimeError,
            match="Simulated database failure",
        ):
            call_command(
                "import_wdi",
                file=str(csv_path),
                expected_rows=1,
            )

    assert Indicator.objects.count() == 0
    assert IndicatorObservation.objects.count() == 0
