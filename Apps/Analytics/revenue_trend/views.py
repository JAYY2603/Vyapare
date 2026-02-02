from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    RevenueTrendChartResponseSerializer,
    RevenueTrendQuerySerializer,
    RevenueTrendYearsResponseSerializer,
)
from .service import (
    RevenueTrendServiceError,
    get_available_years,
    get_revenue_trend,
)


def _resolve_user_dataset_path(user_id, dataset_key):
    safe_name = Path(dataset_key).name
    user_folder = Path(settings.DATASET_STORAGE_ROOT) / \
        "uploaded_datasets" / str(user_id)
    target_path = (user_folder / safe_name).resolve()

    try:
        target_path.relative_to(user_folder.resolve())
    except ValueError:
        return None

    if not target_path.exists() or not target_path.is_file():
        return None

    return target_path


@extend_schema(
    responses={200: RevenueTrendYearsResponseSerializer},
    tags=["Analytics"],
    description="Fetch available years for Revenue Trend analytics.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_revenue_trend_years(request, dataset_key):
    dataset_path = _resolve_user_dataset_path(request.user.id, dataset_key)
    if dataset_path is None:
        return Response(
            {"message": "Dataset not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        years = get_available_years(dataset_path)
    except RevenueTrendServiceError as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"years": years}, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[RevenueTrendQuerySerializer],
    responses={200: RevenueTrendChartResponseSerializer},
    tags=["Analytics"],
    description="Fetch Revenue Trend data for selected year and optional month.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_revenue_trend_chart(request, dataset_key):
    dataset_path = _resolve_user_dataset_path(request.user.id, dataset_key)
    if dataset_path is None:
        return Response(
            {"message": "Dataset not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    query_serializer = RevenueTrendQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {
                "message": "Please fix the highlighted errors.",
                "errors": query_serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    validated = query_serializer.validated_data
    year = validated["year"]
    month = validated.get("month")

    try:
        trend_data = get_revenue_trend(
            dataset_path,
            year=year,
            month=month,
        )
    except RevenueTrendServiceError as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "year": year,
            "month": month,
            "granularity": trend_data["granularity"],
            "total_revenue": trend_data["total_revenue"],
            "points": trend_data["points"],
        },
        status=status.HTTP_200_OK,
    )
