from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserChangePasswordView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path(
        "change-password/",
        UserChangePasswordView.as_view(),
        name="user-change-password",
    ),
]
