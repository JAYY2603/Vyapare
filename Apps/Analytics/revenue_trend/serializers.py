from rest_framework import serializers


class RevenueTrendQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class RevenueTrendYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class RevenueTrendPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    revenue = serializers.FloatField()


class RevenueTrendChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(required=False, allow_null=True)
    granularity = serializers.ChoiceField(choices=["month", "day"])
    total_revenue = serializers.FloatField()
    points = RevenueTrendPointSerializer(many=True)
