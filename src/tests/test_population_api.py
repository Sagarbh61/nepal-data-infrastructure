
import pytest
from rest_framework.test import APIClient

from population.models import LocalGovernmentPopulation


@pytest.mark.django_db
def test_population_api_returns_population_records():
    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="Province-1",
        district_name="Taplejung",
        local_government_name="Phaktanlung Gaunpalika",
        households=2832,
        population_total=11791,
        population_male=6088,
        population_female=5703,
    )

    client = APIClient()
    response = client.get("/api/population/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["population_total"] == 11791


@pytest.mark.django_db
def test_population_api_filters_by_province():
    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="Province-1",
        district_name="Taplejung",
        local_government_name="Municipality A",
        households=100,
        population_total=400,
        population_male=210,
        population_female=190,
    )

    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=2,
        district_code=2,
        local_government_code=1,
        province_name="Province-2",
        district_name="District B",
        local_government_name="Municipality B",
        households=200,
        population_total=700,
        population_male=360,
        population_female=340,
    )

    client = APIClient()
    response = client.get("/api/population/?province_code=1")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["province_code"] == 1


@pytest.mark.django_db
def test_population_api_filters_by_district():
    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="Province-1",
        district_name="District A",
        local_government_name="Municipality A",
        households=100,
        population_total=400,
        population_male=210,
        population_female=190,
    )

    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=1,
        district_code=2,
        local_government_code=2,
        province_name="Province-1",
        district_name="District B",
        local_government_name="Municipality B",
        households=200,
        population_total=700,
        population_male=360,
        population_female=340,
    )

    client = APIClient()
    response = client.get("/api/population/?district_code=1")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["district_code"] == 1

@pytest.mark.django_db
def test_population_api_paginates_records():
    for code in range(1, 102):
        district_code = ((code - 1) // 98) + 1
        local_government_code = ((code - 1) % 98) + 1

        LocalGovernmentPopulation.objects.create(
            census_year=2021,
            province_code=1,
            district_code=district_code,
            local_government_code=local_government_code,
            province_name="Province-1",
            district_name="District A",
            local_government_name=f"Municipality {code}",
            households=100,
            population_total=400,
            population_male=210,
            population_female=190,
        )

    client = APIClient()
    response = client.get("/api/population/")

    assert response.status_code == 200
    assert response.data["count"] == 101
    assert len(response.data["results"]) == 100
    assert response.data["next"] is not None

    second_page = client.get("/api/population/?page=2")

    assert second_page.status_code == 200
    assert len(second_page.data["results"]) == 1
    assert second_page.data["previous"] is not None
    assert second_page.data["next"] is None

@pytest.mark.django_db
def test_population_api_rejects_non_integer_province_code():
      client = APIClient()

      response = client.get(
          "/api/population/?province_code=abc"
      )

      assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_rejects_non_integer_district_code():
    client = APIClient()

    response = client.get(
        "/api/population/?district_code=abc"
    )
    assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_rejects_out_of_range_province_code():
    client = APIClient()

    response = client.get(
        "/api/population/?province_code=999"
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_rejects_districts_outside_province():
    client = APIClient()

    response = client.get(
        "/api/population/?province_code=1&district_code=77"
    )
    assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_accepts_district_without_province():
    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=7,
        district_code=72,
        local_government_code=1,
        province_name="Province-7",
        district_name="District 72",
        local_government_name="Municipality 72",
        households=100,
        population_total=400,
        population_male=210,
        population_female=190,
    )
    client = APIClient()
    response = client.get(
        "/api/population/?district_code=72"
    )

    assert response.status_code == 200
    assert response.data["count"] > 0

    for record in response.data["results"]:
        assert record["district_code"] == 72


@pytest.mark.django_db
def test_population_api_includes_census_year():
    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="Province-1",
        district_name="Taplejung",
        local_government_name="Municipality A",
        households=100,
        population_total=400,
        population_male=210,
        population_female=190,
    )

    response = APIClient().get("/api/population/")

    assert response.status_code == 200
    assert response.data["results"][0]["census_year"] == 2021

@pytest.mark.django_db
def test_population_api_includes_census_year():
    LocalGovernmentPopulation.objects.create(
        census_year=2021,
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="Province-1",
        district_name="Taplejung",
        local_government_name="Municipality A",
        households=100,
        population_total=400,
        population_male=210,
        population_female=190,
    )

    response = APIClient().get("/api/population/")

    assert response.status_code == 200
    assert response.data["results"][0]["census_year"] == 2021


@pytest.mark.django_db
def test_population_api_filters_by_local_government():
    for code, name in [(1, "Municipality A"), (2, "Municipality B")]:
        LocalGovernmentPopulation.objects.create(
            census_year=2021,
            province_code=1,
            district_code=1,
            local_government_code=code,
            province_name="Province-1",
            district_name="Taplejung",
            local_government_name=name,
            households=100,
            population_total=400,
            population_male=210,
            population_female=190,
        )

    response = APIClient().get(
        "/api/population/?local_government_code=2"
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["local_government_code"] == 2
    assert response.data["results"][0]["local_government_name"] == "Municipality B"

@pytest.mark.django_db
def test_population_api_rejects_non_positive_district_code():
    client = APIClient()
    response = client.get("/api/population/?district_code=0")

    assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_rejects_unknown_district_codes():
    client = APIClient()
    response = client.get("/api/population/?district_code=999")

    assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_filters_by_census_year():
    client = APIClient()

    LocalGovernmentPopulation.objects.create(
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="koshi",
        district_name="sample district",
        local_government_name="sample municipality",
        households=100,
        population_total=400,
        population_male=200,
        population_female=200,
        census_year=2021,
    )

    LocalGovernmentPopulation.objects.create(
        province_code=1,
        district_code=1,
        local_government_code=1,
        province_name="koshi",
        district_name="sample district",
        local_government_name="sample municipality",
        households=100,
        population_total=500,
        population_male=250,
        population_female=250,
        census_year=2022,
    )

    response = client.get("/api/population/?census_year=2021")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["census_year"] == 2021

@pytest.mark.django_db
def test_population_api_rejects_non_integer_census_year():
    client = APIClient()

    response = client.get("/api/population/?census_year=abc")

    assert response.status_code == 400

@pytest.mark.django_db
def test_population_api_rejects_non_positive_census_year():
    client = APIClient()

    response = client.get("/api/population/?census_year=0")

    assert response.status_code == 400