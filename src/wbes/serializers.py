
from rest_framework import serializers


class WBESObstacleSerializer(serializers.Serializer):
    obstacle = serializers.CharField()
    label = serializers.CharField()
    weight = serializers.CharField()
    total_records = serializers.IntegerField()
    valid_responses = serializers.IntegerField()
    excluded_responses = serializers.IntegerField()
    major_or_severe_responses = serializers.IntegerField()
    unweighted_share = serializers.FloatField()
    weighted_share = serializers.FloatField()
