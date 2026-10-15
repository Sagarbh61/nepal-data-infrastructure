
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from indicators.models import Indicator, IndicatorObservation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_indicator(db):
    return Indicator.objects.create(
        code="NY.GDP.MKTP.KD.ZG",
        name="GDP growth",
        source="World Development Indicators",
    )


@pytest.fixture
def sample_observation(db, sample_indicator):
    return IndicatorObservation.objects.create(
        indicator=sample_indicator,
        country_code="NPL",
        year=2020,
        value=Decimal("2.345678901234567890123456789"),
    )


@pytest.mark.django_db
def test_indicator_list_returns_expected_fields(
    api_client, sample_indicator
):
    response = api_client.get("/api/indicators/")

    assert response.status_code == 200
    assert response.data["count"] == 1

    result = response.data["results"][0]
    assert result["code"] == "NY.GDP.MKTP.KD.ZG"
    assert result["name"] == "GDP growth"
    assert result["source"] == "World Development Indicators"


@pytest.mark.django_db
def test_indicator_detail_uses_indicator_code(
    api_client, sample_indicator
):
    response = api_client.get(
        "/api/indicators/NY.GDP.MKTP.KD.ZG/"
    )

    assert response.status_code == 200
    assert response.data["code"] == sample_indicator.code


@pytest.mark.django_db
def test_observation_filtering_preserves_decimal_value(
    api_client, sample_observation
):
    response = api_client.get(
        "/api/observations/",
        {
            "country_code": "npl",
            "year": "2020",
            "indicator_code": "NY.GDP.MKTP.KD.ZG",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1

    result = response.data["results"][0]
    assert result["country_code"] == "NPL"
    assert result["year"] == 2020
    assert result["indicator_code"] == "NY.GDP.MKTP.KD.ZG"
    assert result["value"] == "2.345678901234567890123456789"


@pytest.mark.django_db
def test_observation_endpoint_rejects_invalid_year(
    api_client,
):
    response = api_client.get(
        "/api/observations/",
        {"year": "not-a-year"},
    )

    assert response.status_code == 400
    assert "year" in response.data


@pytest.mark.django_db
def test_observation_endpoint_rejects_invalid_country_code(
    api_client,
):
    response = api_client.get(
        "/api/observations/",
        {"country_code": "NP"},
    )

    assert response.status_code == 400
    assert "country_code" in response.data


@pytest.mark.django_db
def test_observation_endpoint_is_paginated(
    api_client, sample_indicator
):
    observations = [
        IndicatorObservation(
            indicator=sample_indicator,
            country_code="NPL",
            year=1960 + offset,
            value=Decimal(offset),
        )
        for offset in range(101)
    ]
    IndicatorObservation.objects.bulk_create(observations)

    response = api_client.get("/api/observations/")

    assert response.status_code == 200
    assert response.data["count"] == 101
    assert len(response.data["results"]) == 100
    assert response.data["next"] is not None
