from django.urls import path

from . import views
from .payment_method_split import views as payment_method_split_views
from .revenue_split_by_payment_method import views as revenue_split_views
from .revenue_trend import views as revenue_trend_views

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
    path(
        "analytics/api/revenue-split-by-payment-method/<str:dataset_key>/years/",
        revenue_split_views.api_revenue_split_years,
        name="api_revenue_split_years",
    ),
    path(
        "analytics/api/revenue-split-by-payment-method/<str:dataset_key>/chart/",
        revenue_split_views.api_revenue_split_chart,
        name="api_revenue_split_chart",
    ),
    path(
        "analytics/api/revenue-trend/<str:dataset_key>/years/",
        revenue_trend_views.api_revenue_trend_years,
        name="api_revenue_trend_years",
    ),
    path(
        "analytics/api/revenue-trend/<str:dataset_key>/chart/",
        revenue_trend_views.api_revenue_trend_chart,
        name="api_revenue_trend_chart",
    ),
]
