from django.db.models.signals import post_save
from django.dispatch import receiver
from cart.models import Cart
from accounts.models import User


@receiver(post_save, sender=User)
def create_cart_for_customer(sender, instance, created, **kwargs):
    if created and instance.role == 'CUSTOMER':
        Cart.objects.create(user=instance)
