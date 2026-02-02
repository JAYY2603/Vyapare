from django.urls import path

from . import views
from .payment_method_split import views as payment_method_split_views

app_name = "analytics"

urlpatterns = [
    path("analytics/upload/", views.upload_dataset, name="upload_dataset"),
    path(
        "analytics/generated/<str:dataset_key>/",
        views.generated_analytics,
        name="generated_analytics",
    ),
    path(
        "analytics/api/payment-method-split/<str:dataset_key>/years/",
        payment_method_split_views.api_payment_method_split_years,
        name="api_payment_method_split_years",
    ),
    path(
        "analytics/api/payment-method-split/<str:dataset_key>/chart/",
        payment_method_split_views.api_payment_method_split_chart,
        name="api_payment_method_split_chart",
    ),
]
