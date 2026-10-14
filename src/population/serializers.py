from rest_framework import serializers

from population.models import LocalGovernmentPopulation

class LocalGovernmentPopulationSerializer(serializers.ModelSerializer):
  class Meta:
    model = LocalGovernmentPopulation
    fields = [
      "census_year",
      "province_code",
      "district_code",
      "local_government_code",
      "province_name",
      "district_name",
      "local_government_name",
      "households",
      "population_total",
      "population_male",
      "population_female",
    ]
