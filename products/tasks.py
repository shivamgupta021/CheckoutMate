# products/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
from accounts.models import User


@shared_task
def check_low_quantity_products():
    low_quantity_products = Product.objects.filter(quantity__lt=10)
    if low_quantity_products:
        employees = User.objects.filter(role=User.Role.EMPLOYEE)
        employee_emails = [employee.email for employee in employees]

        subject = "Low Product Quantity Alert"
        message = "The following products have quantity below 10:\n\n"
        for product in low_quantity_products:
            message += f"{product.name}: {product.quantity}\n"

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                employee_emails,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")


@shared_task
def send_daily_product_update():
    products = Product.objects.all()
    employees = User.objects.filter(role=User.Role.EMPLOYEE)
    employee_emails = [employee.email for employee in employees]

    subject = "Daily Product Update"
    message = "Here's the current product inventory:\n\n"
    for product in products:
        message += f"{product.name}: {product.quantity}\n"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        employee_emails,
        fail_silently=False,
    )
