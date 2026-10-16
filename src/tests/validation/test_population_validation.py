
from ndi.validation.validate_population import validate_keys_and_hierarchy
from ndi.validation.validate_population import normalize_name


def make_record(line, codes, row_type, province_name="Province A"):
    prov, dist, gapa = codes

    return {
        "line": line,
        "codes": codes,
        "type": row_type,
        "raw": {
            "provname": province_name,
            "dname": "District A",
            "gapaname": "Local Government A",
        },
        "values": {
            "nHhld": 10,
            "total": 100,
            "male": 49,
            "female": 51,
        },
    }


def test_duplicate_geographic_keys_are_reported():
    records = [
        make_record(2, (1, 0, 0), "province"),
        make_record(3, (1, 0, 0), "province"),
    ]
    issues = []

    validate_keys_and_hierarchy(records, issues)

    assert any("Duplicate geographic key" in issue for issue in issues)


def test_missing_province_aggregate_is_reported():
    records = [
        make_record(2, (1, 1, 0), "district"),
    ]
    issues = []

    validate_keys_and_hierarchy(records, issues)

    assert any("province aggregate missing" in issue for issue in issues)


def test_inconsistent_province_names_are_detected():
    records = [
        make_record(2, (1, 0, 0), "province", "Province A"),
        make_record(3, (2, 0, 0), "province", "Province B"),
        make_record(4, (1, 1, 0), "district", "Province Different"),
    ]
    issues = []

    validate_keys_and_hierarchy(records, issues)

    assert any("province name" in issue.lower() for issue in issues)

def test_name_normalization_ignores_punctuation_and_case():
    assert normalize_name("PROVINCE - 1") == normalize_name("Province-1")