from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsEmployeeOrReadOnly
from accounts.renderers import ErrorRenderer


class ProductViewSet(viewsets.ModelViewSet):
    renderer_classes = [ErrorRenderer]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsEmployeeOrReadOnly]
