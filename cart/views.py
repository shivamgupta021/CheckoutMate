from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product
from .permissions import IsCustomer
from accounts.renderers import ErrorRenderer
from drf_spectacular.utils import extend_schema


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    renderer_classes = [ErrorRenderer]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    @extend_schema(exclude=True)
    def retrieve(self, request, pk=None):
        pass

    @extend_schema(exclude=True)
    def create(self, request):
        pass

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def partial_update(self, serializer):
        pass

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        pass

    def get_user_cart(self):
        return Cart.objects.get(user=self.request.user)

    @extend_schema(
        description="Add an item to the authenticated user's cart",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "quantity": {"type": "integer", "default": 1},
                },
                "required": ["product_id"]
            }
        },
        responses={200: CartItemSerializer},
    )
    @action(detail=False, methods=["post"])
    def add_item(self, request, pk=None):
        cart = self.get_user_cart()
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

    @extend_schema(
        description="Update the quantity of an item in the authenticated user's cart",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "quantity": {"type": "integer", "default": 1},
                },
                "required": ["product_id", "quantity"]
            }
        },
        responses={200: CartItemSerializer}
    )
    @action(detail=False, methods=["patch"])
    def update_item_quantity(self, request, pk=None):
        cart = self.get_user_cart()
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

    @extend_schema(
        description="Remove an item from the authenticated user's cart",
        responses={204: None}
    )
    @action(detail=False, methods=["delete"], url_path="remove_item/(?P<product_id>\d+)")
    def remove_item(self, request, pk=None):
        cart = self.get_user_cart()
        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
