from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from .forms import LoginForm, RegisterForm
from .serializers import (
    LoginResponseSerializer,
    LoginSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
)


def home(request):
    return render(request, "home/home.html")


def simple_page(request, title, message):
    context = {
        "title": title,
        "message": message,
    }
    return render(request, "home/simple_page.html", context)


def register(request):
    return render(request, "home/register.html", {"form": RegisterForm()})


def login(request):
    if request.user.is_authenticated:
        return redirect("dataset:dataset_list")
    return render(request, "home/login.html", {"form": LoginForm()})


def logout(request):
    auth_logout(request)
    return redirect("home:home")


@login_required
def trends(request):
    return simple_page(request, "Trends", "Trends page is coming soon.")


@login_required
def analytics(request):
    return simple_page(request, "Analytics", "Analytics page is coming soon.")


@login_required
def user_chatbot(request):
    return simple_page(request, "Chatbot", "Chatbot page is coming soon.")


@login_required
def admin_dashboard(request):
    return simple_page(request, "Users", "Admin dashboard page is coming soon.")


@login_required
def account(request):
    return simple_page(request, "Account", "Account page is coming soon.")

############################################## API endpoint for user registration ##############################################


@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterResponseSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def api_register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "message": "Please fix the highlighted errors.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    return Response(
        {
            "message": "Registration successful.",
            "user_id": user.id,
            "redirect_url": "/login/",
        },
        status=status.HTTP_201_CREATED,
    )

############################################## API endpoint for user login ##############################################


@extend_schema(
    request=LoginSerializer,
    responses={200: LoginResponseSerializer},
    tags=["Authentication"],
    description="Authenticate a user with email and password.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        non_field_errors = serializer.errors.get("non_field_errors")
        if non_field_errors:
            return Response(
                {
                    "message": non_field_errors[0],
                    "errors": serializer.errors,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "message": "Please fix the highlighted errors.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.validated_data["user"]
    auth_login(request, user)

    return Response(
        {
            "message": "Login successful.",
            "redirect_url": "/datasets/",
        }
    )
