from django.db import models
from django.contrib.auth.models import User


class PredictionDataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_validated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.file_name} - {self.user.username}"

    class Meta:
        ordering = ['-uploaded_at']


class Prediction(models.Model):
    dataset = models.ForeignKey(
        PredictionDataset, on_delete=models.CASCADE, related_name='predictions')
    prediction_result = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction - {self.dataset.id} at {self.generated_at}"

    class Meta:
        ordering = ['-generated_at']
