from django.urls import path

from . import views

app_name = "predictions"

urlpatterns = [
    path("predictions/upload/", views.upload_dataset, name="upload_dataset"),
    path("api/predictions/generate/", views.api_generate_predictions,
         name="api_generate_predictions"),
]
