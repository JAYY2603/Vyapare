from rest_framework import serializers


class PaymentVsCategoryQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=True, min_value=1900, max_value=3000)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class PaymentVsCategoryYearsResponseSerializer(serializers.Serializer):
    years = serializers.ListField(child=serializers.IntegerField())


class PaymentVsCategoryCellSerializer(serializers.Serializer):
    payment_method = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class PaymentVsCategoryRowSerializer(serializers.Serializer):
    category = serializers.CharField()
    total_records = serializers.IntegerField()
    split = PaymentVsCategoryCellSerializer(many=True)


class PaymentVsCategoryChartResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField(required=False, allow_null=True)
    total_records = serializers.IntegerField()
    payment_methods = serializers.ListField(child=serializers.CharField())
    categories = PaymentVsCategoryRowSerializer(many=True)
