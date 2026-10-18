
import csv

import pytest
from rest_framework.test import APIClient

from wbes import views


ENDPOINT = "/api/wbes/business-obstacles/"

FIELDS = [
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


def make_record(index=1):
    return {
        "obstacle": f"test_{index}",
        "label": f"Test obstacle {index}",
        "weight": "wmedian",
        "total_records": "582",
        "valid_responses": "580",
        "excluded_responses": "2",
        "major_or_severe_responses": "120",
        "unweighted_share": "0.20",
        "weighted_share": "0.25",
    }


def write_csv(path, records, fieldnames=FIELDS):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_wbes_endpoint_returns_obstacle_fields(client, tmp_path, monkeypatch):
    csv_path = tmp_path / "business_obstacles.csv"
    write_csv(csv_path, [make_record()])
    monkeypatch.setattr(views, "WBES_FILE", csv_path)

    response = client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.data["count"] == 1

    result = response.data["results"][0]
    assert result["obstacle"] == "test_1"
    assert result["weight"] == "wmedian"
    assert result["weighted_share"] == 0.25
    assert result["unweighted_share"] == 0.2


@pytest.mark.django_db
def test_wbes_endpoint_uses_pagination(client, tmp_path, monkeypatch):
    csv_path = tmp_path / "business_obstacles.csv"
    write_csv(csv_path, [make_record(i) for i in range(105)])
    monkeypatch.setattr(views, "WBES_FILE", csv_path)

    response = client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.data["count"] == 105
    assert len(response.data["results"]) == 100
    assert response.data["next"] is not None


@pytest.mark.django_db
def test_wbes_endpoint_handles_missing_file(client, tmp_path, monkeypatch):
    missing_file = tmp_path / "missing.csv"
    monkeypatch.setattr(views, "WBES_FILE", missing_file)

    response = client.get(ENDPOINT)

    assert response.status_code == 500
    assert response.data["detail"] == (
        "The processed WBES dataset is unavailable or invalid."
    )


@pytest.mark.django_db
def test_wbes_endpoint_rejects_invalid_csv_data(
    client, tmp_path, monkeypatch
):
    csv_path = tmp_path / "business_obstacles.csv"
    record = make_record()
    record["weighted_share"] = "not-a-number"
    write_csv(csv_path, [record])
    monkeypatch.setattr(views, "WBES_FILE", csv_path)

    response = client.get(ENDPOINT)

    assert response.status_code == 500
    assert response.data["detail"] == (
        "The processed WBES dataset is unavailable or invalid."
    )

def test_wbes_metadata_returns_methodology_and_limitations(client):
    response = client.get("/api/wbes/metadata/")

    assert response.status_code == 200
    assert response.data["survey"] == (
        "World Bank Enterprise Survey, Nepal 2023"
    )
    assert response.data["weighting"]["primary_weight"] == "wmedian"
    assert "major or severe" in response.data["measure"]
    assert any(
        "not represent every business" in limitation
        for limitation in response.data["limitations"]
    )


def test_wbes_metadata_documents_perception_limitation(client):
    response = client.get("/api/wbes/metadata/")

    assert response.status_code == 200
    assert any(
        "causal effects" in limitation
        for limitation in response.data["limitations"]
    )

def test_wbes_metadata_explains_excluded_response_categories(client):
    response = client.get("/api/wbes/metadata/")

    assert response.status_code == 200

    limitations = response.data["limitations"]
    exclusion_note = next(
        (
            limitation
            for limitation in limitations
            if "excluded count combines these categories" in limitation
        ),
        None,
    )

    assert exclusion_note is not None
    assert "not applicable (-7)" in exclusion_note
    assert "don't know (-9)" in exclusion_note
