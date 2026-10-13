
from django.db import models
from django.db.models import F, Q


class LocalGovernmentPopulation(models.Model):
    province_code = models.PositiveSmallIntegerField()
    district_code = models.PositiveSmallIntegerField()
    local_government_code = models.PositiveSmallIntegerField()

    province_name = models.CharField(max_length=100)
    district_name = models.CharField(max_length=100)
    local_government_name = models.CharField(max_length=150)

    households = models.PositiveIntegerField()
    population_total = models.PositiveIntegerField()
    population_male = models.PositiveIntegerField()
    population_female = models.PositiveIntegerField()

    census_year = models.PositiveSmallIntegerField(default=2021)

    class Meta:
        ordering = [
            "province_code",
            "district_code",
            "local_government_code",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "census_year",
                    "province_code",
                    "district_code",
                    "local_government_code",
                ],
                name="unique_local_government_census",
            ),
            models.CheckConstraint(
                condition=Q(local_government_code__gte=1)
                & Q(local_government_code__lte=98),
                name="valid_local_government_code",
            ),
            models.CheckConstraint(
                condition=Q(
                    population_total=(
                        F("population_male") + F("population_female")
                    )
                ),
                name="population_sex_totals_match",
            ),
        ]

    def __str__(self):
        return (
            f"{self.local_government_name}, "
            f"{self.district_name} ({self.census_year})"
        )