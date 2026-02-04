from rest_framework import serializers


class OrderVolumeQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)


class OrderVolumeYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class OrderVolumePointSerializer(serializers.Serializer):
    day = serializers.IntegerField()
    count = serializers.IntegerField()


class OrderVolumeChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    days_in_month = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    points = OrderVolumePointSerializer(many=True)
