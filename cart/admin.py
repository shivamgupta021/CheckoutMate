from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "item_count", "total_price", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__email", "user__name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Number of Items"

    def total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    total_price.short_description = "Total Price"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "quantity"]
    list_filter = ["cart__user"]
    search_fields = ["cart__user__email", "product__name"]
