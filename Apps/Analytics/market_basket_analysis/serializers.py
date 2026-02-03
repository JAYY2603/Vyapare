from rest_framework import serializers


class MarketBasketAnalysisQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)


class MarketBasketAnalysisYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class MarketBasketAnalysisPointSerializer(serializers.Serializer):
    label = serializers.CharField()
    count = serializers.IntegerField()


class MarketBasketAnalysisChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    total_pair_occurrences = serializers.IntegerField()
    points = MarketBasketAnalysisPointSerializer(many=True)
