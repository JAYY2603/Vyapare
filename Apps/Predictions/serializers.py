from rest_framework import serializers
from .models import PredictionDataset, Prediction


class UploadPredictionDatasetSerializer(serializers.Serializer):
    dataset_file = serializers.FileField()


class PredictionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    prediction_id = serializers.IntegerField()
    prediction_result = serializers.JSONField()
    generated_at = serializers.DateTimeField()


class PredictionDatasetResponseSerializer(serializers.Serializer):
    dataset_id = serializers.IntegerField()
    file_name = serializers.CharField()
    uploaded_at = serializers.DateTimeField()
    is_validated = serializers.BooleanField()


class GeneratePredictionSerializer(serializers.Serializer):
    dataset_id = serializers.IntegerField()
