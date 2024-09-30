from django.core.mail import EmailMessage
from django.conf import settings
from celery import shared_task


@shared_task
def send_bill_email(bill_id, user_email, pdf_content):
    email = EmailMessage(
        subject=f"Bill for Order {bill_id}",
        body="Please find attached the bill for your recent order.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.attach(f"bill_{bill_id}.pdf", pdf_content, "application/pdf")
    email.send()
