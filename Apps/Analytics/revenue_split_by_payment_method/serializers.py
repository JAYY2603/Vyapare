from rest_framework import serializers


class RevenueSplitByPaymentMethodQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class RevenueSplitByPaymentMethodYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class RevenueSplitByPaymentMethodChartSliceSerializer(serializers.Serializer):
    payment_method = serializers.CharField()
    revenue = serializers.FloatField()
    percentage = serializers.FloatField()


class RevenueSplitByPaymentMethodChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(required=False, allow_null=True)
    total_revenue = serializers.FloatField()
    split = RevenueSplitByPaymentMethodChartSliceSerializer(many=True)
