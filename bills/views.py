from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.template.loader import get_template
from io import BytesIO
from .tasks import send_bill_email
from xhtml2pdf import pisa
from django.db import transaction
from products.models import Product
from .models import Bill, BillItem
from .serializers import BillSerializer
from cart.models import Cart, CartItem
from accounts.renderers import ErrorRenderer
from drf_spectacular.utils import extend_schema
from cart.permissions import IsCustomer
from django.db.models import F, Prefetch


class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsCustomer]
    renderer_classes = [ErrorRenderer]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Bill.objects.none()
        return Bill.objects.prefetch_related(
            Prefetch("bills", queryset=BillItem.objects.select_related('product'))
        ).filter(user=self.request.user)

    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        pass

    @extend_schema(exclude=True)
    def generate_pdf(self, template_src, context_dict):
        """
        Generates a PDF from the given template and context.
        """
        template = get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return result.getvalue()
        return None

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def generate_bill(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).prefetch_related(
            Prefetch("items", queryset=CartItem.objects.select_related('product'))
        ).first()

        if not cart or not cart.items.exists():
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = list(cart.items.all())
        product_ids = [item.product_id for item in cart_items]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        bill = Bill.objects.create(user=user, total_amount=total_amount)

        bill_items = []
        products_to_update = []

        for cart_item in cart_items:
            product = products[cart_item.product_id]
            if product.quantity < cart_item.quantity:
                transaction.set_rollback(True)
                return Response(
                    {"error": f"Not enough stock for {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            bill_items.append(
                BillItem(
                    bill=bill,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.price,
                )
            )

            product.quantity = F('quantity') - cart_item.quantity
            products_to_update.append(product)

        BillItem.objects.bulk_create(bill_items)
        Product.objects.bulk_update(products_to_update, ['quantity'])

        cart.items.all().delete()

        context = {
            "bill": bill,
            "user": user,
            "cart_items": cart_items,
        }
        pdf = self.generate_pdf("bills/bill_pdf.html", context)

        if pdf:
            send_bill_email.delay(bill.id, user.email, pdf)

        serializer = self.get_serializer(bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
