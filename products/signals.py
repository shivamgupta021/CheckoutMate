from .tasks import check_low_quantity_products
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Product


@receiver(post_save, sender=Product)
def check_product_quantity(sender, instance, **kwargs):
    if instance.quantity < 10:
        check_low_quantity_products.delay()
