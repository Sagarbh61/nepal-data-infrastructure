
import csv
import pytest

from ndi.transformation.wdi import transform_wdi_csv


def test_transform_wdi_csv_converts_wide_data_to_long_format(tmp_path):
    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "processed" / "wdi_output.csv"

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "2021",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            "2.3",
            "4.1",
            "",
        ],
    ]

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    output_count = transform_wdi_csv(input_path, output_path)

    with output_path.open("r", encoding="utf-8", newline="") as file:
        output_rows = list(csv.DictReader(file))

    assert output_count == 2
    assert len(output_rows) == 2

    assert output_rows[0] == {
        "country_name": "Nepal",
        "country_code": "NPL",
        "indicator_name": "GDP growth (annual %)",
        "indicator_code": "NY.GDP.MKTP.KD.ZG",
        "year": "2020",
        "value": "2.3",
    }

    assert output_rows[1] == {
        "country_name": "Nepal",
        "country_code": "NPL",
        "indicator_name": "GDP growth (annual %)",
        "indicator_code": "NY.GDP.MKTP.KD.ZG",
        "year": "2021",
        "value": "4.1",
    }

    assert output_path.exists()


def test_transform_wdi_csv_preserves_missing_values_as_blank(tmp_path):
    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "wdi_output.csv"

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "2021",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            "2.3",
            "",
            "",
        ],
    ]

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    output_count = transform_wdi_csv(input_path, output_path)

    with output_path.open("r", encoding="utf-8", newline="") as file:
        output_rows = list(csv.DictReader(file))

    assert output_count == 2
    assert output_rows[0]["value"] == "2.3"
    assert output_rows[1]["year"] == "2021"
    assert output_rows[1]["value"] == ""

def test_transform_wdi_csv_rejects_non_numeric_values(tmp_path):
    import pytest

    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "wdi_output.csv"

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "2021",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            "2.3",
            "unknown",
            "",
        ],
    ]

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    with pytest.raises(ValueError, match="Non-numeric value"):
        transform_wdi_csv(input_path, output_path)



def test_transform_wdi_csv_rejects_unexpected_headers(tmp_path):
    import pytest

    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "wdi_output.csv"

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            "2.3",
            "",
        ],
    ]

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    with pytest.raises(ValueError, match="Unexpected WDI column headers"):
        transform_wdi_csv(input_path, output_path)


def test_transform_wdi_csv_rejects_rows_with_wrong_column_count(tmp_path):
    import pytest

    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "wdi_output.csv"

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "2021",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            "2.3",
        ],
    ]

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    with pytest.raises(ValueError, match="columns"):
        transform_wdi_csv(input_path, output_path)


@pytest.mark.parametrize("invalid_value", ["NaN", "inf", "-inf"])
def test_transform_wdi_csv_rejects_non_finite_values(
    tmp_path, invalid_value
):
    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "wdi_output.csv"

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            invalid_value,
            "",
        ],
    ]

    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    with pytest.raises(ValueError, match="Non-finite value"):
        transform_wdi_csv(input_path, output_path)


def test_transform_wdi_csv_does_not_overwrite_output_when_validation_fails(
    tmp_path,
):
    input_path = tmp_path / "wdi_input.csv"
    output_path = tmp_path / "wdi_output.csv"

    # This file represents a previously successful transformation.
    original_output = "existing valid output\n"
    output_path.write_text(original_output, encoding="utf-8")

    source_rows = [
        ["Data Source", "World Development Indicators", ""],
        [],
        ["Last Updated Date", "2026-10-08", ""],
        [],
        [
            "Country Name",
            "Country Code",
            "Indicator Name",
            "Indicator Code",
            "2020",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "GDP growth (annual %)",
            "NY.GDP.MKTP.KD.ZG",
            "5.2",
            "",
        ],
        [
            "Nepal",
            "NPL",
            "Invalid indicator",
            "TEST.INVALID",
            "not-a-number",
            "",
        ],
    ]

    with input_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerows(source_rows)

    with pytest.raises(ValueError, match="Non-numeric value"):
        transform_wdi_csv(input_path, output_path)

    assert output_path.read_text(encoding="utf-8") == original_output
