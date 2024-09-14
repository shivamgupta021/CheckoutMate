from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Bill, BillItem
from .serializers import BillSerializer
from cart.models import Cart
from products.models import Product
from django.db import transaction


class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bill.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def generate_bill(self, request):
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()

        if not cart_items:
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = 0
        bill = Bill.objects.create(user=user, total_amount=total_amount)

        for cart_item in cart_items:
            product = cart_item.product
            if product.quantity < cart_item.quantity:
                transaction.set_rollback(True)
                return Response(
                    {"error": f"Not enough stock for {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            BillItem.objects.create(
                bill=bill,
                product=product,
                quantity=cart_item.quantity,
                price=product.price,
            )

            total_amount += product.price * cart_item.quantity
            product.quantity -= cart_item.quantity
            product.save()

        bill.total_amount = total_amount
        bill.save()

        cart.items.all().delete()  # Clear the cart

        serializer = self.get_serializer(bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
