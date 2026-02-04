from django.urls import path

from . import views
from .category_performance import views as category_performance_views
from .day_wise_pattern import views as day_wise_pattern_views
from .market_basket_analysis import views as market_basket_views
from .order_volume import views as order_volume_views
from .payment_method_split import views as payment_method_split_views
from .revenue_split_by_payment_method import views as revenue_split_views
from .revenue_trend import views as revenue_trend_views
from .top_selling_items import views as top_selling_items_views

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
    path(
        "analytics/api/category-performance/<str:dataset_key>/years/",
        category_performance_views.api_category_performance_years,
        name="api_category_performance_years",
    ),
    path(
        "analytics/api/category-performance/<str:dataset_key>/chart/",
        category_performance_views.api_category_performance_chart,
        name="api_category_performance_chart",
    ),
    path(
        "analytics/api/market-basket-analysis/<str:dataset_key>/years/",
        market_basket_views.api_market_basket_years,
        name="api_market_basket_years",
    ),
    path(
        "analytics/api/market-basket-analysis/<str:dataset_key>/chart/",
        market_basket_views.api_market_basket_chart,
        name="api_market_basket_chart",
    ),
    path(
        "analytics/api/top-selling-items/<str:dataset_key>/years/",
        top_selling_items_views.api_top_selling_items_years,
        name="api_top_selling_items_years",
    ),
    path(
        "analytics/api/top-selling-items/<str:dataset_key>/chart/",
        top_selling_items_views.api_top_selling_items_chart,
        name="api_top_selling_items_chart",
    ),
    path(
        "analytics/api/order-volume/<str:dataset_key>/years/",
        order_volume_views.api_order_volume_years,
        name="api_order_volume_years",
    ),
    path(
        "analytics/api/order-volume/<str:dataset_key>/chart/",
        order_volume_views.api_order_volume_chart,
        name="api_order_volume_chart",
    ),
    path(
        "analytics/api/day-wise-pattern/<str:dataset_key>/years/",
        day_wise_pattern_views.api_day_wise_pattern_years,
        name="api_day_wise_pattern_years",
    ),
    path(
        "analytics/api/day-wise-pattern/<str:dataset_key>/chart/",
        day_wise_pattern_views.api_day_wise_pattern_chart,
        name="api_day_wise_pattern_chart",
    ),
]
