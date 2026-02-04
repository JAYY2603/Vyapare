from rest_framework import serializers


class DayWisePatternQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)


class DayWisePatternYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class DayWisePatternBucketSerializer(serializers.Serializer):
    sales_count = serializers.IntegerField()
    sales_amount = serializers.FloatField()
    intensity = serializers.FloatField()


class DayWisePatternDaySerializer(serializers.Serializer):
    day = serializers.IntegerField()
    morning = DayWisePatternBucketSerializer()
    daytime = DayWisePatternBucketSerializer()
    evening = DayWisePatternBucketSerializer()


class DayWisePatternChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    days_in_month = serializers.IntegerField()
    total_sales_count = serializers.IntegerField()
    total_sales_amount = serializers.FloatField()
    points = DayWisePatternDaySerializer(many=True)
