import random
from django.core.exceptions import ValidationError
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsEmployeeOrReadOnly
from accounts.renderers import ErrorRenderer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from faker import Faker
from rest_framework.response import Response
from rest_framework import status
import faker_commerce
from rest_framework import pagination

fake = Faker()
fake.add_provider(faker_commerce.Provider)


@extend_schema(
    request=ProductSerializer,
    responses=ProductSerializer,
    examples=[
        OpenApiExample(
            "New Product Example",
            value={
                "name": fake.ecommerce_name(),
                "description": fake.text(),
                "price": (random.randint(5000, 10000) / 100),
                "quantity": random.randint(100, 1000),
            },
            description="Example to create a new product listing. Requires employee authentication.",
        ),
    ],
)
class ProductViewSet(viewsets.ModelViewSet):
    renderer_classes = [ErrorRenderer]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsEmployeeOrReadOnly]
    pagination_class = pagination.PageNumberPagination

    def create(self, request, *args, **kwargs):
        product_name = request.data.get('name')
        if Product.objects.filter(name=product_name).exists():
            raise ValidationError({"detail": "A product with this name already exists."})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
