from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.template.loader import get_template
from io import BytesIO
from django.core.mail import EmailMessage
from xhtml2pdf import pisa
from django.db import transaction
from .models import Bill, BillItem
from .serializers import BillSerializer
from cart.models import Cart
from django.conf import settings
from accounts.renderers import ErrorRenderer
from drf_spectacular.utils import extend_schema


class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ErrorRenderer]

    @extend_schema(exclude=True)
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Bill.objects.none()
        return Bill.objects.filter(user=self.request.user)

    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

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

        cart.items.all().delete()

        context = {
            "bill": bill,
            "user": user,
            "cart_items": cart_items,
        }
        pdf = self.generate_pdf("bills/bill_pdf.html", context)

        if pdf:
            # Send the PDF via email
            email = EmailMessage(
                subject=f"Bill for Order {bill.id}",
                body="Please find attached the bill for your recent order.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )

            email.attach(f"bill_{bill.id}.pdf", pdf, "application/pdf")
            email.send()

        serializer = self.get_serializer(bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
