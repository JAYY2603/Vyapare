from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("analytics/upload/", views.upload_dataset, name="upload_dataset"),
    path(
        "analytics/generated/<str:dataset_name>/",
        views.generated_analytics,
        name="generated_analytics",
    ),
]
