from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from .permissions import IsCustomer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_item_quantity(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get("product_id")
        new_quantity = int(request.data.get("quantity", 1))

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get("product_id")

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "This action is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
