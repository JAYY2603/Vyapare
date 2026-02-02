from rest_framework import serializers


class PaymentMethodSplitQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class PaymentMethodSplitYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class PaymentMethodSplitChartSliceSerializer(serializers.Serializer):
    payment_method = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class PaymentMethodSplitChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(required=False, allow_null=True)
    total_records = serializers.IntegerField()
    split = PaymentMethodSplitChartSliceSerializer(many=True)
