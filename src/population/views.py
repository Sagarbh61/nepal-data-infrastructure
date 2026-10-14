from rest_framework import generics
from rest_framework.exceptions import ValidationError

from population.serializers import LocalGovernmentPopulationSerializer
from population.models import LocalGovernmentPopulation

class LocalGovernmentPopulationListView(generics.ListAPIView):
  serializer_class = LocalGovernmentPopulationSerializer

  def get_queryset(self):
    queryset = LocalGovernmentPopulation.objects.all().order_by(
      "province_code",
      "district_code",
      "local_government_code",
    )

    province_code = self.request.query_params.get("province_code")
    district_code = self.request.query_params.get("district_code")
    local_government_code = self.request.query_params.get("local_government_code")
    census_year = self.request.query_params.get("census_year")

    if census_year is not None:
      try:
        census_year = int(census_year)
      except ValueError:
        raise ValidationError("The census year must be an integer.")

      if census_year < 1:
        raise ValidationError("The census year must be positive.")

      queryset = queryset.filter(census_year=census_year)

    if province_code is not None:
      try:
        province_code = int(province_code)
      except ValueError:
        raise ValidationError("The province code must be an integer.")

      if province_code < 1 or province_code > 7:
        raise ValidationError("The province code must be between 1 and 7.")

      queryset = queryset.filter(province_code=province_code)

    if district_code is not None:
      try:
        district_code = int(district_code)
      except ValueError:
        raise ValidationError("The district code must be an integer.")

      if district_code < 1:
        raise ValidationError("The district code must be a positive integer.")

      district_queryset = LocalGovernmentPopulation.objects.filter(district_code=district_code)

      if province_code is not None:
        district_queryset = district_queryset.filter(province_code=province_code)

      if not district_queryset.exists():
        raise ValidationError("The specified district does not exist for the selected province.")

      queryset = queryset.filter(district_code=district_code)


    if local_government_code is not None:
      try:
        local_government_code = int(local_government_code)
      except ValueError:
        raise ValidationError("The local government code must be an integer.")

      if local_government_code < 1 or local_government_code > 98:
        raise ValidationError("The local government code must be between 1 and 98.")

      queryset = queryset.filter(local_government_code=local_government_code)


    return queryset
