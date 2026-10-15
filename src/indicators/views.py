from rest_framework import generics
from rest_framework.exceptions import ValidationError

from indicators.models import IndicatorObservation, Indicator
from indicators.serializers import IndicatorSerializer, IndicatorObservationSerializer

class IndicatorListView(generics.ListAPIView):
  queryset = Indicator.objects.all()
  serializer_class = IndicatorSerializer

class IndicatorDetailView(generics.RetrieveAPIView):
  queryset = Indicator.objects.all()
  serializer_class = IndicatorSerializer
  lookup_field = "code"

class IndicatorObservationListView(generics.ListAPIView):
  serializer_class = IndicatorObservationSerializer

  def get_queryset(self):
    queryset = IndicatorObservation.objects.select_related("indicator")

    country_code = self.request.query_params.get("country_code")
    year = self.request.query_params.get("year")
    indicator_code = self.request.query_params.get("indicator_code")

    if country_code is not None:
      country_code = country_code.strip().upper()

      if(
        len(country_code)!=3
        or not country_code.isascii()
        or not country_code.isalpha()
      ):
        raise ValidationError(
          {
            "country_code": ("Provide a valid three letter country code"
        )}
        )

      queryset = queryset.filter(country_code=country_code)

    if year is not None:
      try:
        year = int(year)
      except ValueError:
        raise ValidationError(
          {
            "year": "The year must be an integer"
          }
        )

      if not 1960 <= year <=2100:
        raise ValidationError(
          {
            "year": "The year must be in between 1960 and 2100."
          }
        )

      queryset = queryset.filter(year=year)

    if indicator_code is not None:
      indicator_code = indicator_code.strip()

      if not indicator_code:
        raise ValidationError(
          {
            "indicator_code":"The indicator code cannot be empty"
          }
        )

      queryset = queryset.filter(indicator__code = indicator_code)

    return queryset
