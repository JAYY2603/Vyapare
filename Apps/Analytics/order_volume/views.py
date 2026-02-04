from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    OrderVolumeChartResponseSerializer,
    OrderVolumeQuerySerializer,
    OrderVolumeYearsResponseSerializer,
)
from .service import (
    OrderVolumeServiceError,
    get_available_years,
    get_order_volume_by_day,
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
    responses={200: OrderVolumeYearsResponseSerializer},
    tags=["Analytics"],
    description="Fetch available years for Order Volume analytics.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_volume_years(request, dataset_key):
    dataset_path = _resolve_user_dataset_path(request.user.id, dataset_key)
    if dataset_path is None:
        return Response(
            {"message": "Dataset not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        years = get_available_years(dataset_path)
    except OrderVolumeServiceError as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"years": years}, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[OrderVolumeQuerySerializer],
    responses={200: OrderVolumeChartResponseSerializer},
    tags=["Analytics"],
    description="Fetch monthly Order Volume heatmap data for selected year and month.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_volume_chart(request, dataset_key):
    dataset_path = _resolve_user_dataset_path(request.user.id, dataset_key)
    if dataset_path is None:
        return Response(
            {"message": "Dataset not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    query_serializer = OrderVolumeQuerySerializer(data=request.query_params)
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
    month = validated["month"]

    try:
        chart_data = get_order_volume_by_day(
            dataset_path,
            year=year,
            month=month,
        )
    except OrderVolumeServiceError as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "year": year,
            "month": month,
            "days_in_month": chart_data["days_in_month"],
            "total_orders": chart_data["total_orders"],
            "points": chart_data["points"],
        },
        status=status.HTTP_200_OK,
    )
