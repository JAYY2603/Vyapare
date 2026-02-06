from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import ChatbotDatasetUploadSerializer, ChatbotMessageRequestSerializer
from .service import (
    ChatbotServiceError,
    build_dataset_context,
    generate_business_reply,
)


@login_required
def chatbot_page(request):
    return render(request, "chatbot/chatbot.html")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_chatbot_upload_dataset(request):
    serializer = ChatbotDatasetUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    uploaded_file = serializer.validated_data["file"]
    try:
        dataset_context, dataset_meta = build_dataset_context(uploaded_file)
    except ValueError as exc:
        return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    request.session["chatbot_dataset_context"] = dataset_context
    request.session["chatbot_dataset_meta"] = dataset_meta
    request.session.modified = True

    return Response(
        {
            "message": "Dataset uploaded successfully.",
            "dataset": dataset_meta,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_chatbot_message(request):
    serializer = ChatbotMessageRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_message = serializer.validated_data["message"]
    history = serializer.validated_data.get("history", [])
    dataset_context = request.session.get("chatbot_dataset_context", "")

    if not dataset_context:
        return Response(
            {
                "reply": "Please upload an Excel or CSV dataset first, then ask questions about that dataset."
            },
            status=status.HTTP_200_OK,
        )

    try:
        reply = generate_business_reply(
            user_message, history, dataset_context=dataset_context)
    except ChatbotServiceError as exc:
        payload = {"message": exc.message}
        if exc.detail:
            payload["detail"] = exc.detail
        return Response(payload, status=exc.status_code)

    return Response({"reply": reply}, status=status.HTTP_200_OK)
