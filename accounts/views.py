from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .renderers import ErrorRenderer
from accounts.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserChangePasswordSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from faker import Faker
import random

fake = Faker()
employee_email = fake.email()
customer_email = fake.email()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [ErrorRenderer]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses=UserRegistrationSerializer,
        examples=[
            OpenApiExample(
                "Employee Example",
                value={
                    "role": "EMPLOYEE",
                    "name": fake.name(),
                    "age": random.randint(18, 60),
                    "email": employee_email,
                    "password": "supersecretpassword",
                    "password2": "supersecretpassword",
                },
                description="Example of an employee.",
            ),
            OpenApiExample(
                "Customer Example",
                value={
                    "role": "CUSTOMER",
                    "name": fake.name(),
                    "age": random.randint(18, 60),
                    "email": customer_email,
                    "password": "supersecretpassword",
                    "password2": "supersecretpassword",
                },
                description="Example of a customer.",
            ),
        ],
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {"token": token, "message": "Registration Successful!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [ErrorRenderer]
    serializer_class = UserLoginSerializer

    @extend_schema(
        request=UserLoginSerializer,
        responses=UserLoginSerializer,
        examples=[
            OpenApiExample(
                "Employee Example",
                value={
                    "email": employee_email,
                    "password": "supersecretpassword",
                    "password2": "supersecretpassword",
                },
                description="Example of an employee.",
            ),
            OpenApiExample(
                "Customer Example",
                value={
                    "email": customer_email,
                    "password": "supersecretpassword",
                    "password2": "supersecretpassword",
                },
                description="Example of a customer.",
            ),
        ],
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response(
                    {"token": token, "message": "Login Successful!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"errors": {"non_field_errors": ["Invalid email or password."]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChangePasswordView(APIView):
    renderer_classes = [ErrorRenderer]
    permission_classes = [IsAuthenticated]
    serializer_class = UserChangePasswordSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses=UserRegistrationSerializer,
        examples=[
            OpenApiExample(
                "Change Password Example",
                value={
                    "password": "notsosecretpassword",
                    "password2": "notsosecretpassword",
                },
                description="Example of a changed password. Requires authentication.",
            ),
        ],
    )
    def post(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"message": "Password changed successfully!"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
