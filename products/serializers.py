from rest_framework import serializers
from .models import Product
from decimal import Decimal


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
