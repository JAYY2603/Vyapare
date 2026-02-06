from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("api/register/", views.api_register, name="api_register"),
    path("api/login/", views.api_login, name="api_login"),
    path("trends/", views.trends, name="trends"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("account/", views.account, name="account"),
]
