
from rest_framework import serializers

from indicators.models import Indicator, IndicatorObservation


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        fields = ["code", "name", "source"]

class NormalizedDecimalField(serializers.DecimalField):
    def to_representation(self, value):
        if value is None:
            return None

        value = value.normalize()
        return format(value, "f")

class IndicatorObservationSerializer(serializers.ModelSerializer):
    indicator_code = serializers.CharField(
        source="indicator.code",
        read_only=True,
    )
    value = NormalizedDecimalField(
        max_digits=43,
        decimal_places=29,
        allow_null=True,
    )

    class Meta:
        model = IndicatorObservation
        fields = [
            "indicator_code",
            "country_code",
            "year",
            "value",
        ]
