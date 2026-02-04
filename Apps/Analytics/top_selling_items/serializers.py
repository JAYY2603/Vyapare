from rest_framework import serializers


class TopSellingItemsQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class TopSellingItemsYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class TopSellingItemsPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    quantity = serializers.IntegerField()


class TopSellingItemsChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(required=False, allow_null=True)
    total_quantity = serializers.IntegerField()
    points = TopSellingItemsPointSerializer(many=True)
