from rest_framework import serializers


class ChatbotMessageRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000, trim_whitespace=True)
    history = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )

    def validate_message(self, value):
        cleaned = (value or "").strip()
        if not cleaned:
            raise serializers.ValidationError("Message is required.")
        return cleaned


class ChatbotDatasetUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        filename = (getattr(value, "name", "") or "").lower()
        if not filename.endswith((".xlsx", ".xls", ".csv")):
            raise serializers.ValidationError(
                "Unsupported file format. Please upload .xlsx, .xls, or .csv files."
            )

        max_size = 10 * 1024 * 1024
        if getattr(value, "size", 0) > max_size:
            raise serializers.ValidationError(
                "File is too large. Maximum allowed size is 10MB.")

        return value
