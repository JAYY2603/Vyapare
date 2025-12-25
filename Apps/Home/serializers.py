from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=300)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_full_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Full name is required.")
        return cleaned

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        full_name = validated_data["full_name"]
        name_parts = full_name.split(None, 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        return User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]
        user = User.objects.filter(email__iexact=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user_id = serializers.IntegerField()
    redirect_url = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    redirect_url = serializers.CharField()
