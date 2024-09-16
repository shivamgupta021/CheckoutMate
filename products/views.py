import random

from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsEmployeeOrReadOnly
from accounts.renderers import ErrorRenderer
from drf_spectacular.utils import extend_schema, OpenApiExample
from faker import Faker
import faker_commerce

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

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        pass
