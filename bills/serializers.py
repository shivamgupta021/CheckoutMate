from rest_framework import serializers
from .models import Bill, BillItem
from products.serializers import ProductSerializer


class BillItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = BillItem
        fields = ["id", "product", "quantity", "price"]


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ["id", "user", "total_amount", "items", "created_at"]
        read_only_fields = ["user", "total_amount", "created_at"]
