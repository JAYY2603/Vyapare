from pathlib import Path

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    MarketBasketAnalysisChartResponseSerializer,
    MarketBasketAnalysisQuerySerializer,
    MarketBasketAnalysisYearsResponseSerializer,
)
from .service import (
    MarketBasketAnalysisServiceError,
    get_available_years,
    get_frequently_bought_together,
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
    responses={200: MarketBasketAnalysisYearsResponseSerializer},
    tags=["Analytics"],
    description="Fetch available years for Market Basket Analysis.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_market_basket_years(request, dataset_key):
    dataset_path = _resolve_user_dataset_path(request.user.id, dataset_key)
    if dataset_path is None:
        return Response(
            {"message": "Dataset not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        years = get_available_years(dataset_path)
    except MarketBasketAnalysisServiceError as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"years": years}, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[MarketBasketAnalysisQuerySerializer],
    responses={200: MarketBasketAnalysisChartResponseSerializer},
    tags=["Analytics"],
    description="Fetch frequently bought together item pairs for selected year.",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_market_basket_chart(request, dataset_key):
    dataset_path = _resolve_user_dataset_path(request.user.id, dataset_key)
    if dataset_path is None:
        return Response(
            {"message": "Dataset not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    query_serializer = MarketBasketAnalysisQuerySerializer(
        data=request.query_params)
    if not query_serializer.is_valid():
        return Response(
            {
                "message": "Please fix the highlighted errors.",
                "errors": query_serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    year = query_serializer.validated_data["year"]

    try:
        basket_data = get_frequently_bought_together(dataset_path, year=year)
    except MarketBasketAnalysisServiceError as exc:
        return Response(
            {"message": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "year": year,
            "total_pair_occurrences": basket_data["total_pair_occurrences"],
            "points": basket_data["points"],
        },
        status=status.HTTP_200_OK,
    )
