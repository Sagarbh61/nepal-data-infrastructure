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
      queryset = queryset.filter(district_code=district_code)

    if district_code is not None and province_code is not None:
      if not LocalGovernmentPopulation.objects.all().filter(district_code=district_code, province_code=province_code).exists():
        raise ValidationError("This combination of province code and district code does not exists.")

    return queryset
